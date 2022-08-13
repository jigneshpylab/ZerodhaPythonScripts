def cancell_open_order(indx):
    try :
        df = kite.orders()
        df=pd.DataFrame.from_dict(df)
        df = df[df['tradingsymbol'].str.startswith("{}".format(indx))]
        if not df.empty:
            df = df[['order_id','status',"tradingsymbol",'quantity']]
            dfo = df[(df['status'] == 'OPEN') |
                     (df['status'] == 'OPEN PENDING')|
                     (df['status'] == 'VALIDATION PENDING') |
                     (df['status'] == 'PUT ORDER REQ RECEIVED') |
                     (df['status'] == 'MODIFIED')|
                     (df['status'] == 'MODIFY PENDING')|
                     (df['status'] == 'MODIFY VALIDATION PENDING') |
                     (df['status'] == 'MODIFY VALIDATION PENDING') |
                     (df['status'] == 'MODIFY VALIDATION PENDING') |
                     (df['status'] == 'MODIFY VALIDATION PENDING') |
                     (df['status'] == 'TRIGGER PENDING')
                     ]
            for oid in list(dfo.order_id.values):
                try:
                    kite.cancel_order(variety="regular",order_id=oid)
                    print("Order cancelled {}".format(oid))
                except Exception as e :
                    print("cancell_open_order ERROR {}".format(e))

    except Exception as e:
        print("cancell_open_order ERROR {}".format(e))
