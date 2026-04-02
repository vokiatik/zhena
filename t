now update picture screening process.

i need a several process being handled by this page. 

first is current process of picture verificaation from the file.
next one is the same process but file list would be taken from cloud and all the pictures would be on that cloud folder. 
next one is same pictures but only from the cloud folder. And they will have only 2 attributes. format and weekly_price. 

first two are independent, but the last one is being handeled after the second one. 

so what are we gonna do. 

first create a table with process_types
id
process_type_name

second create a table with process_statuses
id
process_status_name

i need u to create a table with the name of processes. 
it will theese columns:
id
type_id (from process_type) table
status_id
comment
initiator_id
created_at

after file uploading we will be adding a row to that table with the type of "file" and filename in the comment and status of initiated.

then u will write a frontend page to upload a link for the second process. It will have only link input field and a create process button. On this button press it will be adding a row to the table with type link and link in the comment and status of initiated. (avaliable to admin and marketing_analyst)

then on row with the type link status being changed to done it will add another row to that table with type analyst and status initiated and  comment with amount of pictures to proceed (selected from ). 

then u will create a frontend page with a list of this processes. it should be updatable by admin and just being displayed for other users. 

marketing_analyst are alowed to proceed to the process of type file or link. Analyst  alowed to proceed to the procees of type analyst. Admin are alowed to update any of this processes by pressing an update button or to proceed. 

on proceed users are being redirected to picture screening page. 

on type file data will be taken from file and that is all. The process from picture_processing_model (rename that file to picture_processing_settings_model) 


i need u to update picture processing. 

we will start with renaming models from picture_processing to process_settings. then rename title column of picture_processing_model to type. Do not forget to update the code everywhere. 

