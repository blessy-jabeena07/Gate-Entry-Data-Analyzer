import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Label, Entry, StringVar, OptionMenu, Frame
from tkinter.messagebox import showinfo
from datetime import datetime

def apply_time_filter(df, start_time, end_time):
    df_copy = df.copy()
    df_copy['In Time'] = pd.to_datetime(df_copy['In Time'], format='%H:%M:%S', errors='coerce')
    df_copy['Out Time'] = pd.to_datetime(df_copy['Out Time'], format='%H:%M:%S', errors='coerce')
    return df_copy[
        ((df_copy['In Time'].dt.hour >= start_time) & (df_copy['In Time'].dt.hour < end_time)) |
        ((df_copy['Out Time'].dt.hour >= start_time) & (df_copy['Out Time'].dt.hour < end_time))
    ]

def apply_date_filter(df, date_value):
    df_copy = df.copy()
    formats = ['%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_value, fmt).strftime('%Y-%m-%d')
            break
        except ValueError:
            continue
    else:
        showinfo("Date Format Error", "Use: YYYY-MM-DD, DD-MM-YYYY, MM-DD-YYYY")
        return df_copy
    if 'Date' in df_copy.columns:
        df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')
        return df_copy[df_copy['Date'].dt.strftime('%Y-%m-%d') == parsed_date]
    else:
        showinfo("Column Error", "Date column not found.")
        return df_copy

def apply_single_filter(df, filter_by, filter_value):
    df_copy = df.copy()
    if not filter_value:
        showinfo("Input Error", "Enter a filter value.")
        return df_copy
    try:
        if filter_by == "Name" and "Name" in df_copy.columns:
            return df_copy[df_copy['Name'].str.contains(filter_value, case=False, na=False)]
        elif filter_by == "Email" and "Email" in df_copy.columns:
            return df_copy[df_copy['Email'].str.contains(filter_value, case=False, na=False)]
        elif filter_by == "Mobile No" and "Mobile No" in df_copy.columns:
            return df_copy[df_copy['Mobile No'].astype(str).str.contains(filter_value, na=False)]
        elif filter_by == "Date":
            return apply_date_filter(df_copy, filter_value)
        elif filter_by == "Time":
            try:
                start_time, end_time = map(int, filter_value.split('-'))
                if 0 <= start_time <= 23 and 0 <= end_time <= 24:
                    return apply_time_filter(df_copy, start_time, end_time)
                else:
                    showinfo("Time Range Error", "Hours must be between 0 and 23.")
            except ValueError:
                showinfo("Format Error", "Format: start-end (e.g., 9-17)")
        elif filter_by == "Gender" and "Gender" in df_copy.columns:
            return df_copy[df_copy['Gender'].str.contains(filter_value, case=False, na=False)]
        elif filter_by == "Month" and "Month" in df_copy.columns:
            df_copy['Month'] = df_copy['Month'].astype(str)
            return df_copy[df_copy['Month'].str.contains(filter_value, case=False, na=False)]
        return df_copy
    except Exception as e:
        print(f"Filter Error: {e}")
        showinfo("Error", f"Filter Error: {e}")
        return df_copy

def visualize_by_column(df, column):
    counts = df[column].value_counts()
    if not counts.empty:
        plt.figure(figsize=(10, 5))
        counts.plot(kind='pie', autopct=lambda p: f'{int(p * sum(counts) / 100)}', startangle=90)
        plt.title(f'Distribution of {column}')
        plt.ylabel('')
        plt.tight_layout()
        plt.show()

def visualize_time_distribution(df):
    try:
        in_counts = df['In Time'].dt.hour.value_counts().sort_index()
        out_counts = df['Out Time'].dt.hour.value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(in_counts.index, in_counts.values, marker='o', label='In Time')
        ax.plot(out_counts.index, out_counts.values, marker='s', label='Out Time')
        ax.set_title('In and Out Time Frequency')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Count')
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Time Visualization Error: {e}")
        showinfo("Visualization Error", f"Time plot error: {e}")

def preprocess_dataframe(df):
    df_copy = df.copy()
    if "Date" in df_copy.columns:
        df_copy['Date'] = pd.to_datetime(df_copy['Date'], errors='coerce')
        df_copy['Month'] = df_copy['Date'].dt.strftime('%B')
    for time_col in ['In Time', 'Out Time']:
        if time_col in df_copy.columns:
            df_copy[time_col] = pd.to_datetime(df_copy[time_col], errors='coerce')
    return df_copy

def analyze_data(df, filter_by, filter_value):
    df_filtered = apply_single_filter(df, filter_by, filter_value)
    if df_filtered.empty:
        showinfo("No Data", "No results for selected filter.")
        return
    if filter_by == "Time":
        visualize_time_distribution(df_filtered)
    elif filter_by == "Gender":
        visualize_by_column(df_filtered, 'Gender')
    elif filter_by == "Month":
        df_filtered['Month'] = df_filtered['Month'].astype(str)
        counts = df_filtered['Month'].value_counts().sort_index()
        counts.plot(kind='bar', color='orange')
        plt.title('Entries per Month')
        plt.xlabel('Month')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.show()
    elif filter_by == "Date":
        df_filtered = df_filtered[df_filtered['Out Time'].notna()]
        out_counts = df_filtered.groupby(df_filtered['Date'].dt.date).size()
        if out_counts.empty:
            showinfo("No Data", "No students went out on this date.")
            return
        out_counts.plot(kind='bar', color='salmon')
        plt.title('Students Who Went Out on Date')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.show()
    else:
        visualize_by_column(df_filtered, filter_by)

def main():
    global filter_by_var, filter_value_var, user_type_var

    # Load both CSVs
    hosteller_df = preprocess_dataframe(pd.read_csv(r"C:\Users\bless\Downloads\Hosteller Sheet - Sheet1.csv"))
    visitor_df = preprocess_dataframe(pd.read_csv(r"C:\Users\bless\Downloads\Copy of Visitor.csv"))

    root = Tk()
    root.title("Data Analysis Tool")
    root.geometry("450x400")

    frame = Frame(root, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    Label(frame, text="User Type:").pack()
    user_type_var = StringVar(value="Hosteller")
    OptionMenu(frame, user_type_var, "Hosteller", "Visitor").pack()

    Label(frame, text="Filter By:").pack()
    filter_by_var = StringVar(value="Name")
    filter_menu = OptionMenu(frame, filter_by_var, "Name", "Email", "Date", "Time", "Gender", "Month")
    filter_menu.pack()

    Label(frame, text="Filter Value:").pack()
    filter_value_var = StringVar()
    Entry(frame, textvariable=filter_value_var).pack()

    def update_filter_options(*args):
        user_type = user_type_var.get()
        menu = filter_menu["menu"]
        menu.delete(0, "end")
        if user_type == "Visitor":
            options = ["Name", "Email", "Mobile No"]
        else:
            options = ["Name", "Email", "Date", "Time", "Gender", "Month"]
        for option in options:
            menu.add_command(label=option, command=lambda value=option: filter_by_var.set(value))
        filter_by_var.set(options[0])

    user_type_var.trace_add("write", update_filter_options)

    def analyze_clicked():
        df = visitor_df if user_type_var.get() == "Visitor" else hosteller_df
        analyze_data(df, filter_by_var.get(), filter_value_var.get())

    Button(
        frame,
        text="Analyze Data",
        command=analyze_clicked,
        bg="lightblue"
    ).pack(pady=10)

    def show_filter_info():
        df = visitor_df if user_type_var.get() == "Visitor" else hosteller_df
        f = filter_by_var.get()
        info = f"Selected Filter: {f}\n"
        if f in df.columns:
            values = df[f].dropna().unique()
            info += ", ".join(map(str, values[:10])) + ("..." if len(values) > 10 else "")
        elif f == "Time":
            info += "Enter range: start-end (e.g., 9-17)"
        showinfo("Filter Info", info)

    Button(frame, text="Show Filter Info", command=show_filter_info, bg="lightgreen").pack()

    root.mainloop()

if __name__ == "__main__":
    main()
