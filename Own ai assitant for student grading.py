def grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 75:
        return "A"
    elif marks >= 60:
        return "B"
    elif marks >= 40:
        return "C"
    else:
        return "F"

def student_grading():
    n = int(input("Enter number of subjects: "))
    results = {}
    for i in range(n):
        subject = input(f"Enter subject {i+1} name: ")
        marks = int(input(f"Enter marks for {subject}: "))
        results[subject] = grade(marks)

    print("\n--- Report Card ---")
    for sub, g in results.items():
        print(f"{sub}: {g}")

student_grading()
