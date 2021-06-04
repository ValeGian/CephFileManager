import requests

url = "http://172.16.3.231:8080"

def help():
    print("Available commands are:\n"
          "!help --> shows available commands\n"
          "!list --> retrieve the list of files currently stored in the database\n"
          "!delete <filename> --> delete a file\n"
          "!upload <file_path> --> upload a file\n"
          "!download <filename> --> download a file\n"
          "!statistics --> Shows current statistics on the status of the cluster\n"
          "!exit --> close the client\n"
          "-----------------------------------------")

if __name__ == '__main__':
    help()

    exit = False
    while not exit:
        prompt = input("> ")
        splits = prompt.split()
        if len((splits)) < 1:
            continue

        command = splits[0]

        if command == "!help":
            help()

        elif command == "!list":
            r = requests.get("{}/objects".format(url))
            print(r.text)

        elif command == "!delete":
            filename = splits[1]
            r = requests.delete("{}/objects/{}".format(url, filename))
            print(r.text)

        elif command == "!upload":
            filename = splits[1]
            file = open(filename, 'rb')
            files = {'file': file}
            r = requests.post("{}/objects".format(url), files=files)
            print(r.text)
            file.close()

        elif command == "!download":
            filename = splits[1]
            r = requests.get("{}/objects/{}".format(url, filename))
            if not r.text == "unable to retrieve the object":
                file = open(filename, "wb")
                file.write(r.content)
                file.close()
                print("successfully rerieved file")
            else:
                print(r.text)

        elif command == "!statistics":
            r = requests.get("{}/status".format(url))
            print(r.text)

        elif command == "!exit":
            exit = True

        print("\n")
