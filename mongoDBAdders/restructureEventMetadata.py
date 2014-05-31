import json
import argparse
import sys
import helpers

def main(prodDB='prod',prodRDB='prodR'):
    col = helpers.getCollection(prodDB)
    restructCol = helpers.getCollection(prodRDB,True)
    print ("Restructuring metadata in events")

    events = col.find()

    total = events.count()
    count = 0

    for event in events:
        tmp = event
        if 'event_id' in tmp:
            tmp['event_id'] = event_idMapper(tmp['event_id'])
            restructCol.insert(tmp)
            count += 1
            helpers.printProgress(count,total)

    print ()
    print ("Done restructuring")


def event_idMapper(event_id):
    return {
        'content:interact:product_detail_viewed': 'product_detail_clicked',
        'content:interact:product_clicked': 'product_detail_clicked',
        'content:interact:productClicked': 'product_detail_clicked',
        'content:interact:product_wanted': 'product_wanted',
        'content:interact:productWanted': 'product_wanted',
        'purchase:buy_clicked': 'product_purchase_intended',
        'login:user_logged_in': 'user_logged_in',
        'login:userLoggedIn' : 'user_logged_in',
        "content:explore:collection_clicked": "collection_viewed",
        "content:explore:brandprofile:collections_clicked":"collection_viewed",
        "content:explore:brandprofile: collectionsClicked":"collection_viewed",
        "content:explore:collectionClicked":"collection_viewed",
        "start:appLoaded":"app_started",
        "start:app_loaded":"app_started",
        "navigation:navbar:menu_clicked":"menu_opened",
        "content:explore:brandprofile: allProductsClicked":"storefront_clicked",
        "content:explore:brandprofile:all_products_clicked":"storefront_clicked",
        "content:explore:brand_clicked":"storefront_clicked",
        "content:explore:brandClicked":"storefront_clicked",
        "content:explore:brandprofile:hot_clicked":"storefront_clicked",
        "content:explore:brandprofile:new_clicked":"storefront_clicked",
        "content:explore:brandprofile:sale_clicked":"storefront_clicked",
    }.get(event_id, event_id)

if __name__ == "__main__":
    main()
