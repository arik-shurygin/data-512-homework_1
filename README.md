README
Project Goals:

The goal of this project is to query, process, and analyize wikipedia data on a long list of dinosaur wikipedia pages from June 2015 up until end of August 2022.
All Source data comes from the Wikimedia foundation REST API which queries viewer info on the wikipedia service. The API link is linked below.
https://www.mediawiki.org/wiki/REST_API#Terms_and_conditions


API documentation: https://wikitech.wikimedia.org/wiki/Analytics/AQS/Pageviews#Quick_start


From the API calls all data is processed and output into the dino_monthly_*_<start_date>_<end_date>.csv files. Which split the data by the access type of the viewer. Three different splits are created, cumulative, desktop, and mobile. Desktop refers to desktop viewership metrics only, Mobile for mobile webpages and apps, and cumulative for all sources combined.

The wikipedia_pageview_analysis python file generates three png files, each documenting the Maximum Average and Minimum Average, Top 10 Peak Page Views, and Fewest Months of Data charts. The analysis file DOES EXCLUDE any dinosaur wikipedia pages which the API could not load any data for, impacting in particulr the minimum average chart which could report different values if those dinosaurs were included.
