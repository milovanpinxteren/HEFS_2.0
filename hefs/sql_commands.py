class SqlCommands:
    # def __init__(self, dates):
    #     self.get_veh_command(dates)

    def get_veh_command(self, dates):
        make_veh_command = """
        SELECT "hefs_productinfo"."omschrijving","productID", "productcode",
        """

        for date in dates:
            make_veh_command += f"""
               COALESCE(SUM(CASE
                                WHEN "hefs_orders"."afleverdatum" = '{date[0]}' THEN "hefs_pickitems"."hoeveelheid"
                                ELSE NULL END), NULL) AS "{date[0]}",
            """
        make_veh_command += """
                       COALESCE(SUM("hefs_pickitems"."hoeveelheid")) AS "Totaal"
                    """
        # make_veh_command += f"""COALESCE("hefs_pickitems"."omschrijving", "hefs_pickitems"."productID", "hefs_pickitems"."hoeveelheid"
        #                 JOIN "hefs_productinfo" ON "hefs_productinfo"."productID" = "hefs_pickitems"."product_id")
        #
        #       """
        # make_veh_command = make_veh_command[:-14] + make_veh_command[-13]
        make_veh_command += """FROM "hefs_pickitems"
                     LEFT OUTER JOIN "hefs_productinfo" ON ("hefs_pickitems"."product_id" = "hefs_productinfo"."productID")
                     INNER JOIN "hefs_pickorders" ON ("hefs_pickitems"."pick_order_id" = "hefs_pickorders"."id")
                     INNER JOIN "hefs_orders" ON ("hefs_pickorders"."order_id" = "hefs_orders"."id")
            GROUP BY "hefs_productinfo"."omschrijving","productID"            
        """
        return make_veh_command
