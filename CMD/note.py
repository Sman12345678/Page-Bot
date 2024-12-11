'''
Note Creator and reader by Kolawole Suleiman.
'''
Info={
"Description":"Notepad to write and read notes"
}
def execute():
    def Note(response):
        return response

    user_input = input("Welcome to Notepad on Kora. Reply this with the action you prefer:\n ★Write\n★Read\n")
    
    if user_input.lower() == "write":
        try:
            note_name = input("Enter your file name with .txt extension (like note.txt): ")
            note = input("Reply this message with your note: ")
            with open(note_name, "w") as f:
                f.write(note)
            return Note("🎉 Note written Successfully")
        except Exception as e:
            return f"An Error occurred: {e}"
    
    elif user_input.lower() == "read":
        try:
            read = input("Enter the name of the file to read: ")
            with open(read, "r") as r:
                file = r.read()
            return f"___✨ Here is your file ✨___\n{file}\n__________"
        except Exception as e:
            return f"An Error Occurred: {e}"



