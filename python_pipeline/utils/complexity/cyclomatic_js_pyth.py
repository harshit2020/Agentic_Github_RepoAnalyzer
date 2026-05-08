import lizard

def cyclomatic_js_pyth():
    try:
        analysis_result = lizard.analyze(["./input_code"])

        for file_info in analysis_result:
            print(f"File : {file_info.filename} CCN : {file_info.average_cyclomatic_complexity}") 
    except Exception as e:
        print("Cyclomatic complexity computation error!!")

if __name__ == "__main__":
    cyclomatic_js_pyth()

