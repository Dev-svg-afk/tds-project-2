# curl -X POST "http://localhost:8000/api" -F "questions.txt=@questions/question2.txt"

curl -X POST "http://localhost:8000/api" -F "questions.txt=@questions/question3/questions.txt" -F "sample-sales.csv=@questions/question3/sample-sales.csv"
