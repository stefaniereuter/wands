We build two different wands servers, because of a bug in adios2 (cannot send 1 dimensional arrays) that will only be fixed in adios 2.9. 
At the time of writing adios2 2.9. was not yet released and the bug fix can only be attained by manually merging the bugfix branch into 
the future 2.9. release branch. 

wands_server: 
This is the preferred version with adios2.9. 
The client will specify the dataset directly and therefore has to specify each dataset seperately

wands_server_group:
In the UKAEA .h5 files. The lowest leaf groups (lowest level in the hierarchy) always constist of "data", "time" and "error". 
To avoid the bug in sending 1 dimensional arrays in older adios versions we we assemble a 2 dimensional array with data and time.
Still 