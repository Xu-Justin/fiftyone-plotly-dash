#!/bin/bash

# Start the first process
python3 app_flask.py &
  
# Start the second process
python3 app_dash.py &
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?