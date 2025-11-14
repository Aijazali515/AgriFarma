# PowerShell: use Invoke-WebRequest or curl alias
# Test diagnostic raw=1
Invoke-WebRequest http://127.0.0.1:5000/?raw=1 -UseBasicParsing
# Test normal homepage
Invoke-WebRequest http://127.0.0.1:5000/ -UseBasicParsing