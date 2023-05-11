# Architectural Design

## Python Client

  - Sends POST request to server
  - Received response
  - Extracts port number from JSON response content
  - Opens ADIOS2 socket with given port number
  - Receives data from server via ADIOS2

## C++ Server

  - Accepts POST request
  - Extracts file name and signals from POST data
  - Finds file and loads signals from file
  - Triggers creation of ADIOS2 socket
  - Puts loaded signal data onto socket
  - Sends ADIOS2 port number to client

## REST endpoints

  - / GET
    - returns `{ 'api': <STRING>, 'version': <STRING>, 'endpoints': [ <STRING>, <STRING>, ... ] }`
  - /data POST
    - accepts: `{ 'uri': <STRING>, 'signals': [ <STRING>, <STRING>, ... ] }`
    - returns: `{ 'port': <INTEGER> }`