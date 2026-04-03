now update picture screening process.

i need a several process being handled by this page. 

first is current process of picture verificaation from the file.
next one is the same process but file list would be taken from cloud and all the pictures would be on that cloud folder. 
next one is same pictures but only from the cloud folder. And they will have only 2 attributes. format and weekly_price. 

first two are independent, but the last one is being handeled after the second one. 

so what are we gonna do. 

after file uploading we will be adding a row to that table with the type of "file" and filename in the comment and status of initiated. Update file uploading code to add a row to that table.

then u will write a frontend page to upload a link for the second process. It will have only link input field and a create process button. On this button press it will be adding a row to the table with type link and link in the comment and status of initiated. (page is avaliable to admin and marketing_analyst) then redirected to processes page.

then on row with the type link status being changed to done it will add another row to that table with type analyst and status initiated. 

then u will create a frontend page with a list of this processes. it should be updatable by admin and just being displayed for other users. 

marketing_analyst are alowed to proceed to the process of type file or link. Analyst  alowed to proceed to the procees of type analyst. Admin are alowed to update any of this processes by pressing an update button or to proceed. 

on proceed users are being redirected to picture screening page. 

i need u to add another retale like table but it will be named retail_processed and will have extra columns
user_id
type
process_id

also rename retail_upload_rows to just retail and retail_upload_rows_additional to retail_process_additional

on type file data will be taken from retail table. filter rows so only rows from last uploaded file will be shown. also only unverifyied. and on picture processing it will be marked as verified in retail table and no data will be changed there. But in the retail_processed will be added a row with all the data from frontend and also user_id. Type will be set to file. process_id set to this process id. So u need to update this process code on the backend and frontend.

on type link data will be taken from nowhere. backend row should create a list of objects to verify but with no data. only link should be presented for each picture from folder refering to itself of course. but it should exclude already verified pictures from retail_processed by link i guess. On picture proceeded backend should add a row to retail_processed with type link and all other fields specified. process_id set to this process id. So u need to create this process code on the backend and frontend.

on type analyst data should be taken from retail_processed with type link and only from the last portion (by process_id). process_id set to this process id. So u need to create this process code on the backend and frontend.

statuses will be changed like that:
initiated on process creation. In progress when the first picture being verifyied. done after last picture is verified. 

also if there is a process of verifying in progress u need to select only rows which are not verified yet but from the same group as the last verified picture of that type. 



