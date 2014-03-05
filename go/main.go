package main

import (
  _ "github.com/lib/pq"
  "database/sql"
  "fmt"
  "log"
  "sort"
  "os"
  "runtime/pprof"
  "net/http"
  "html/template"
)

type Product struct {
  Id string
  Name string
  Image string
  Score string
}

var multipliers = map[string]float64 {
  "product_detail_clicked": 1.0,
  "product_wanted": 3.0,
  "product_purchase_intended": 5.0,
}

const (
  USER_ID string = "702654506"
)

func addEventHandler(w http.ResponseWriter, r *http.Request, s SlopeOne, db *sql.DB){
  event_id := r.FormValue("event_id")
  product_id := r.FormValue("product_id")
  user_id := r.FormValue("user_id")
  if (event_id == "" || product_id == "" || user_id == "") {
    http.Redirect(w, r, "/", 302)
    return
  }

  // Insert event to DB.
  stmt, _ := db.Prepare(`INSERT INTO sobazar (
                          event_id,
                          product_id,
                          user_id,
                          server_environment
                         )
                         VALUES ($1, $2, $3, 'manual')`)
  _, err := stmt.Exec(event_id, product_id, user_id)
  if (err != nil) { fmt.Fprintf(w, err.Error()) }

  http.Redirect(w, r, "/?userid=" + user_id, 302)
}

func indexPageHandler(w http.ResponseWriter, r *http.Request, s SlopeOne, db *sql.DB){
  user_id := r.FormValue("userid")
  if (user_id == ""){
    user_id = USER_ID
  }
  my_ratings := getProductRatings(user_id, db)

  if (len(my_ratings) == 0) {
    // We do not know anything about the user, and can thus not compute
    // Average distances to other products. Hence we select the item which
    // Has the most ratings and use the average of this item, as a baseline.
    var id string
    var avg float64
    err := db.QueryRow(`SELECT
      t.product_id, ((cnt_prod_wanted*2.0) + (cnt_prod_clicked) + (cnt_prod_purch*5.0))/cnt
      AS average
      FROM (
        SELECT
          product_id,
          count(event_id) as cnt,
          sum(case when event_id = 'product_wanted' then 1 else 0 end) AS cnt_prod_wanted,
          sum(case when event_id = 'product_detail_clicked' then 1 else 0 end) AS cnt_prod_clicked,
          sum(case when event_id = 'product_purchase_intended' then 1 else 0 end) AS cnt_prod_purch
        FROM sobazar
        WHERE product_id != 'NULL'
        AND event_id IN (
          'product_wanted',
          'product_detail_clicked',
          'product_purchase_intended')
        AND server_environment IN ('prod', 'manual')
        GROUP BY product_id
      ) t ORDER BY t.cnt DESC LIMIT 1`).Scan(&id, &avg)
    if (err != nil) { log.Fatal(err) }
    my_ratings[id] = avg
  }

  predictions := s.Predict(my_ratings)
  if len(predictions) == 0 {
    fmt.Fprintf(w, "No results.")
    return
  }
  sort.Sort(ByScore(predictions))

  products := make([]Product, 0)
  for _, pred := range predictions[:10] {
    var product_name string
    err := db.QueryRow(`SELECT DISTINCT product_name
                        FROM sobazar
                        WHERE product_id = $1
                        AND product_name != 'N/A'
                        LIMIT 1`, pred.Title).Scan(&product_name)
    if err != nil { log.Fatal(err) }
    products = append(products, Product{ Name: product_name, Score: pred.Score, Id: pred.Title})
  }

  users := make([]string, 0)
  rows, err := db.Query(`SELECT DISTINCT user_id
                       FROM sobazar
                       WHERE server_environment = 'prod'
                       AND event_id IN (
                        'product_wanted',
                        'product_detail_clicked',
                        'product_purchase_intended')
                      AND random() < 0.01
                      LIMIT 5`)
  if (err != nil) { log.Fatal(err) }
  for rows.Next() {
    var user_id string
    rows.Scan(&user_id)
    users = append(users, user_id)
  }

  t, _ := template.ParseFiles("index.html")
  params := make(map[string]interface{})
  params["recommendedProducts"] = products
  params["userId"] = user_id
  params["users"] = users
  t.Execute(w, params)
}

func getProductRatings(user_id string, db *sql.DB) map[string]float64 {
  /* Input: user_id
     Output: map of product_keys => scores */
 rows, err := db.Query(`SELECT product_id, event_id
                        FROM sobazar
                        WHERE event_id IN (
                          'product_wanted',
                          'product_detail_clicked',
                          'product_purchase_intended'
                        )
                        AND user_id = $1
                        AND server_environment IN ('prod', 'manual')
                        ORDER BY product_id`, user_id)
  if err != nil { log.Fatal(err) }
  m_product_rating := make(map[string]float64)
  for rows.Next() {
    var event_id, product_id string
    err := rows.Scan(&product_id, &event_id)
    if err != nil { log.Fatal(err) }
    m_product_rating[product_id] += (multipliers[event_id] * 1.0)
  }
  return m_product_rating
}

func main(){
  fmt.Println("Cold start! Doing some analysis before serving ...")
  /*
  f, err := os.Create("cpuprofile.prof")
  if err != nil { log.Fatal(err) }
  pprof.StartCPUProfile(f)
  defer pprof.StopCPUProfile()
  */

  multipliers := map[string]float64 {
    "product_detail_clicked": 1.0,
    "product_wanted": 3.0,
    "product_purchase_intended": 5.0,
  }

  // Variables holding all information
  m_users := make(map[string]map[string]float64)
  m_product_rating := make(map[string]float64)

  db, err := sql.Open("postgres", "user=sobazar dbname=sobazar sslmode=disable")
  if err != nil { log.Fatal(err) }
  rows, err := db.Query(`SELECT user_id, product_id, event_id
                         FROM sobazar
                         WHERE event_id IN (
                            'product_wanted',
                            'product_detail_clicked',
                            'product_purchase_intended')
                         AND user_id != 'N/A'
                         AND server_environment IN ('prod', 'manual')
                         ORDER BY user_id, product_id
                         `)
  if err != nil { log.Fatal(err) }
  prev_userid := "-1"
  i := 1
  for rows.Next() {
    var user_id, product_id, event_id string
    err := rows.Scan(&user_id, &product_id, &event_id)
    if (err != nil) { log.Fatal(err) }

    if (user_id != prev_userid && user_id != "-1") {
      // Add the previous user map to "DB" and start a new one.
      m_users[prev_userid] = m_product_rating
      m_product_rating = make(map[string]float64)
      prev_userid = user_id
    }

    m_product_rating[product_id] += (multipliers[event_id] * 1.0)
  }
  // Add the last one too.
  m_users[prev_userid] = m_product_rating

  s := SlopeOne{}
  s.Init()
  i = 1
  for _, ratings := range m_users {
    fmt.Printf("\rUpdating SlopeOne with user %v of %v          ", i, len(m_users))
    s.Update(ratings)
    i += 1
  }
  fmt.Println()
  fmt.Println("Done. Serving webpage at http://locahost:8080/")

  http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
    indexPageHandler(w, r, s, db)
  })
  http.HandleFunc("/add", func(w http.ResponseWriter, r *http.Request) {
    addEventHandler(w, r, s, db)
  })
  http.ListenAndServe(":8080", nil)
}
