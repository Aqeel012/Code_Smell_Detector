import os
import ast
import json
import tkinter as tk
from tkinter import filedialog, messagebox, Button, Label,scrolledtext
import webbrowser

class CodeSmellDetector:
    def __init__(self, project_path):
        self.project_path = project_path
        self.results = []

    def analyze_project(self):
        """
        Traverse the project directory and analyze each Python file.
        """
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)

    def analyze_file(self, file_path):
        """
        Parse the file into an AST and analyze for code smells.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=file_path)
                self.detect_smells(tree, file_path)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
    def detect_smells(self, tree, file_path):
      """
      Detect Large Class, Long Method, Long Parameter List, and Useless Exception Handling.
     """
      for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            self.detect_large_class(node, file_path)
        elif isinstance(node, ast.FunctionDef):
            self.detect_long_method(node, file_path)
            if hasattr(self, 'detect_long_parameter_list'):
                self.detect_long_parameter_list(node, file_path)
        elif isinstance(node, ast.Try):
            if hasattr(self, 'detect_useless_exception_handling'):
                self.detect_useless_exception_handling(node, file_path)


    def detect_large_class(self, node, file_path):
        """
        Detect Large Class: LOC >= 200 or (NOA + NOM) > 40.
        """
        loc = len(node.body)
        noa = sum(1 for n in node.body if isinstance(n, ast.Assign))
        nom = sum(1 for n in node.body if isinstance(n, ast.FunctionDef))

        if loc >= 200 or (noa + nom) > 40:
            self.report_smell("Large Class", file_path, node.lineno, {
                "LOC": loc,
                "NOA": noa,
                "NOM": nom
            })

    def detect_long_method(self, node, file_path):
        """
        Detect Long Method: MLOC >= 100.
        This will count actual lines in the method body, including comments and blank lines.
        """
          
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

         
        start_line = node.lineno - 1   
        end_line = len(lines)

         
        for i in range(start_line + 1, len(lines)):
            if lines[i].strip().startswith("def "):   
                end_line = i
                break

        
        method_lines = lines[start_line:end_line]
        mloc = len(method_lines)

        if mloc >= 100:
            self.report_smell("Long Method", file_path, node.lineno, {
                "MLOC": mloc
            })


    def detect_useless_exception_handling(self, node, file_path):
        """
        Detect Useless Exception Handling: overly general or empty exception handling.
        """
        for handler in node.handlers:
            if isinstance(handler.type, ast.Name) and handler.type.id in ('Exception', 'BaseException'):
                 
                if not handler.body or all(isinstance(stmt, ast.Pass) for stmt in handler.body):
                    self.report_smell("Useless Exception Handling", file_path, node.lineno, {
                        "Type": handler.type.id,
                        "Body": "Empty or Pass"
                    })
    
    def detect_long_parameter_list(self, node, file_path):
        """
        Detect Long Parameter List: PAR >= 5.
        """
        par = len(node.args.args)   
        if par >= 5:
            self.report_smell("Long Parameter List", file_path, node.lineno, {
                "Parameters": par
            })


    def report_smell(self, smell_type, file_path, line_number, details):
        """
        Append detected smell information to the results.
        """
        self.results.append({
            "smell": smell_type,
            "file": file_path,
            "line": line_number,
            "details": details
        })

    def generate_report(self):
        """
        Generate a JSON report of detected code smells.
        """
        report_path = "code_smells_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=4)
        return report_path

 
class CodeSmellDetectorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Code Smell Detector")
        master.geometry("800x600")
        
         
        self.project_frame = tk.Frame(master)
        self.project_frame.pack(padx=10, pady=10, fill=tk.X)
        
        self.project_label = tk.Label(self.project_frame, text="Project Path:")
        self.project_label.pack(side=tk.LEFT)
        
        self.project_path_entry = tk.Entry(self.project_frame, width=50)
        self.project_path_entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        
        self.browse_button = tk.Button(
            self.project_frame, 
            text="Browse", 
            command=self.browse_project
        )
        self.browse_button.pack(side=tk.LEFT)
        
         
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(padx=10, pady=10)
        
        self.analyze_button = tk.Button(
         self.button_frame,
         bg='green',   
         fg='white',   
         text="Analyze",
         command=self.analyze_project,
         width=10,   
         font=('Helvetica', 12, 'bold')   
)

        self.analyze_button.pack(side=tk.LEFT, padx=5)
        
        self.generate_report_button = tk.Button(
            self.button_frame, 
            text="Generate Report", 
            command=self.generate_report,
            state=tk.DISABLED, 
            width=15,   
            font=('Helvetica', 12, 'bold')
        )
        self.generate_report_button.pack(side=tk.LEFT, padx=5)
        
        
        self.results_frame = tk.Frame(master)
        self.results_frame.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        self.results_label = tk.Label(self.results_frame, text="Code Smell Detection Results:")
        self.results_label.pack(anchor="w", padx=5, pady=10)   

        
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20
        )
        self.results_text.pack(expand=True, fill=tk.BOTH)
        
         
        self.status_bar = tk.Label(
            master, 
            text="Ready", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
         
        self.project_path = ""
        self.analysis_results = []
    
    def browse_project(self):
        """Open file dialog to select project directory"""
        folder_path = filedialog.askdirectory(title="Select Python Project Directory")
        if folder_path:
            self.project_path = folder_path
            self.project_path_entry.delete(0, tk.END)
            self.project_path_entry.insert(0, folder_path)
            self.status_bar.config(text=f"Project selected: {folder_path}")
    
    def analyze_project(self):
        """Perform project analysis"""
         
        if not self.project_path or not os.path.isdir(self.project_path):
            messagebox.showerror("Error", "Please select a valid project directory")
            return
        
        
        self.results_text.delete(1.0, tk.END)
        
        try:
             
             
            detector = CodeSmellDetector(self.project_path)
            
             
            detector.analyze_project()
            
             
            self.analysis_results = detector.results
            
            
            self.display_results()
            
             
            self.generate_report_button.config(state=tk.NORMAL)
            
            self.status_bar.config(text="Analysis completed successfully")
        
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
            self.status_bar.config(text="Analysis failed")
    
    def display_results(self):
        """Display detected code smells in results text area"""
        if not self.analysis_results:
            self.results_text.insert(tk.END, "No code smells detected.\n")
            return
        
        for smell in self.analysis_results:
             
            result_text = (
                f"Smell: {smell['smell']}\n"
                f"File: {smell['file']}\n"
                f"Line: {smell['line']}\n"
                f"Details: {json.dumps(smell['details'], indent=2)}\n"
            )
            
             
            self.results_text.insert(tk.END, result_text)
            
             
            self.results_text.insert(tk.END, "\n" + "-" * 50 + "\n\n")
    
    def generate_report(self):
        """Generate detailed JSON report"""
        if not self.analysis_results:
            messagebox.showinfo("Report", "No results to generate report")
            return
        
        
        report_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if report_path:
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(self.analysis_results, f, indent=4)
                
                 
                if messagebox.askyesno("Report Generated", 
                                       "Report saved. Open the file?"):
                    webbrowser.open(report_path)
                
                self.status_bar.config(text=f"Report saved to {report_path}")
            
            except Exception as e:
                messagebox.showerror("Error", f"Could not save report: {e}")

def main():
    root = tk.Tk()
    app = CodeSmellDetectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()