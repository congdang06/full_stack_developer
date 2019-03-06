#!/usr/bin/env python3
import psycopg2
DBNAME = "news"


class Log_Analysis():
    # 1. What are the most popular three articles of all time?
    def display_top_three_popular_articles(self):
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        get_query = "select title, count(title) view_count from articles a \
            join log l on l.path = concat('/article/', a.slug)\
            group by title \
            order by view_count desc \
            limit 3"

        c.execute(get_query)
        result = c.fetchall()
        db.close()
        print("The most popular three articles of all time")
        for i in range(len(result)):
            print("\"" + result[i][0] + "\"" + " -- " + \
            str(result[i][1]) + " views")

    # 2. Who are the most popular article authors of all time?
    def display_most_popular_article_author(self):
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        get_query = "select auth.name, count(auth.name) count_author \
            from articles a \
            join log l on l.path = concat('/article/', a.slug) \
            join authors auth on a.author = auth.id \
            group by auth.name \
            order by count_author desc"
        c.execute(get_query)
        result = c.fetchall()
        db.close()
        print("\nThe most popular article author of all time")
        for i in range(len(result)):
        	print(result[i][0] + " -- " + str(result[i][1]) + " views")

    # 3. On which days did more than 1% of requests lead to errors?
    def display_request_lead_to_errors(self):
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        get_query = " \
          WITH log_time AS(\
          select date(time) as log_date, count(*) as count_log_date \
          from log \
          group by log_date )\
    	    \
          ,error_log_date AS ( \
          select date(time) error_date, count(*) as count_error_date \
          from log \
          where status like '%404%' \
          group by error_date ) \
    	    \
    	    select * \
    	    from ( \
    	        select lt.log_date as return_date, round(cast(100 * elt.count_error_date as numeric) / cast(lt.count_log_date as numeric), 2) as percent_error \
    	        from log_time lt \
    	        left join error_log_date elt on lt.log_date = elt.error_date \
              group by return_date, elt.count_error_date, lt.count_log_date ) as result\
              where percent_error > 1.0 "
        c.execute(get_query)
        result = c.fetchall()
        db.close
        print("\nWhich days did more than 1% of requests lead to errors");
        for i in range(len(result)):
                print(str(result[i][0]) + " -- " + str(result[i][1]) + "% errors")


if __name__ == '__main__':
    la = Log_Analysis()
    # 1. What are the most popular three articles of all time?
    la.display_top_three_popular_articles()
    # 2. Who are the most popular article authors of all time?
    la.display_most_popular_article_author()
    # 3. On which days did more than 1% of requests lead to errors?
    la.display_request_lead_to_errors()