now update the workflow of the whole monthly report operating process.

So we'll have a few tables. 

First one will look like retail but a little bit different. 
its gonna have a:

2. retailer_clean_id
3. avertiser_id
4. brand_id
6. product_category_id
7. brand_category_id
8. First_appearance_date
9. Last_appearance_date
those are data fields, next are technical
0. Addvertisment_id
1. process id
10. data_type (file/link)
11. Verified
12. Declined
13. Created_at

next we'll have a link table:
0. id
1. add_id which is a Addvertisment_id from prev table
2. link
3. appearance_period

next we'll have a table with extra data
0. id
1. add_id which is a Addvertisment_id from prev table
2. brand_id

next we'll have ontoher table with extra data
0. id
1. add_id which is a Addvertisment_id from prev table
2. category_id

next we'll have ontoher table with extra data
0. id
1. add_id which is a Addvertisment_id from prev table
2. Format_id

next we'll have ontoher table with extra data
0. id
1. add_id which is a Addvertisment_id from prev table
2. Add_Category_id

next we'll have ontoher table with extra data
0. id
1. add_id which is a Addvertisment_id from prev table
2. price

next we'll have ontoher table with extra data bools
0. id
1. add_id which is a Addvertisment_id from prev table
2. key_player
3. referent_market
4. packed_chokolate

those were data tables, now we'll go to the dictionaries:
0. column_types_for_simple_values:
currently picture_attribute_reference_type table but needs a refactoring.
will contain values:
avertiser
brand
add_category
product_category
brand_category
retailer_clean
funnel_stage

and fields
id
field_name

1. simple values
currently picture_attribute_reference 
it will cover such a fields as: 
avertiser
brand
add_category
product_category
brand_category
retailer_clean
funnel_stage

and will have a fields
id
column_name_id wchich is an id from column_types_for_simple_values
value

2. formats
identical to ecom_format, but funnel_stage_id should be taken from simple values

3. detector_format_comparison
id
detector_format
format_id which is an id from formats


With all this tables we'll do a process of preparing the data. 

on file upload i need u to write functions to:

1. verify if all the data within the file are presented in the dictionaries:
1.1. simple values:
1.1.1. retailer_clean
1.1.2. avertiser
1.1.3. brand_clean
1.1.4. product_category
1.1.5. brand_category
1.1.6. retailer_clean

1.2 formats:
validate format field by checking if all the values are contained by formats table. If any are not, then check if any are in detector_format_comparison and from that table function need to check if current row format is equal to detector_format and if so should take format_id. 

1.3 brand and category. 
those fields contain form one to several values splited ny god knows what. So they need to be separated according to the brands. So we'll start with slashes braces and semicolons.

if all the values are presented get to parsing step.

if not, user needs to get the list of the values that are not presented. There is a similar functional already existing on file upload. User need to choose either change the value with one from the dictionary or add a new one to the dictionary. For the formats it need to link the new value to any of the existing formats in the detector_format_comparison. Also user should haver a button to add new value to a formats table first if there is no value in formats table. 


data parsing: 
we'll put the values to the tables. 
if there is just one value with current row group_id function shoud first add a row to retail table. Then get add_id of that row to fill other tables. If there are many values we'll do the same but take the values of the first row for the retail table. 

then we'll put links and period to the according table with id we just got. Then other tables should get filled one by one. Then mobe to the next row.

then we'll proceed to the link parsing stage

put a blank func here for now.


So according to this process i need u to rewrite some major modules. 

first of all we'll update process settings. We'll delete all the existing logic. we'll make a script that would handle workflow. it is going to be sustainable. We're not gonna change it from the frontend. 
then we'll gonna rewrite all the existing tables in the reference db. Create all the new files and delete all the old one which are not gonna be required anymore. Then we'll write the process workflow splitting all the functions if it is possible so it would be readable. 
then we'll update the frontend picture processing. 

it's gonna be getting the full data but this data would be collected from different tables on the backend. Then for analyst it's gonna show such fields:

1. brand (brand_id from retail table and name from simple values) and will have a dropdown with all the values from simple_values of category brand 
2. brand_range (id will be get from brand table and name from simple_values table with category_type brand) will have a list of values with delete button and a dropdown with all the values from simple_values of category brand to add new one
3. product_category (product_category from retail table and product_category from simple_values)
4. product_category_range (id will be get from category table and name from simple_values table with category_type product_category) will have a list of values with delete button and a dropdown with all the values from simple_values of category product_category to add new one
5. brand_category (brand_category_id from retail table and name from simple values) and will have a dropdown with all the values from simple_values of category brand_category
6. advertising_category  (from advertising_category table with the value of Add_Category_id and name from simple values with a type of add_category) and a dropdown with values of simple_values of type add_category




