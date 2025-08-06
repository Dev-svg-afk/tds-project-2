def listUnits():
  with open("../response.txt", "r", encoding="utf-8") as resp_file:
      response_parts = resp_file.read().split('\n\n')
  print(response_parts[3])

listUnits()