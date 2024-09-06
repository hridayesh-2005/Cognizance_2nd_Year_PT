import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import mysql.connector

# main window
root = tk.Tk(className='Skyways Flight Management System')
root.geometry("800x600")

# background color to skyblue
root.configure(bg='skyblue')

image = Image.open("background.jpg")
image = image.resize((800,300))
background_image = ImageTk.PhotoImage(image)

background_label = tk.Label(root, image=background_image)
background_label.place(relx=0,rely=1,anchor="sw",relwidth=1, relheight=0.5)

title_label = tk.Label(root, text="Skyways Flight Management System", font=("Helvetica", 24, "bold"), bg='skyblue')
title_label.pack(pady=20)

# frame for buttons
button_frame = tk.Frame(root, bg='skyblue')
button_frame.pack(pady=50)

# SQL connection 
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Hridayesh@2005',
            database='airlines'
        )
        return connection
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

connection = create_connection()
cursor = connection.cursor()

# button functions
def open_user_section():
    title_label.pack_forget()
    button_frame.pack_forget()

    # user section 
    user_frame = tk.Frame(root, bg='skyblue')
    user_frame.pack(pady=50)

    def show_available_flights():
        try:
            cursor.execute("SELECT * FROM available_flights")
            flights = cursor.fetchall()

            flights_window = tk.Toplevel(root)
            flights_window.title("Available Flights")
            flights_window.geometry("800x500") 

            columns = (
                'Flight Number', 'Start Location', 'Destination', 
                'Price', 'Departure Time', 'Arrival Time', 
                'Total Seats', 'Available Seats'
            )
            tree = ttk.Treeview(flights_window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100) 

            tree.pack(expand=True, fill='both')

            for flight in flights:
                tree.insert('', tk.END, values=flight)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def book_ticket():
        def submit_booking():
            user_id = user_id_entry.get()
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            email = email_entry.get()
            phone = phone_entry.get()
            age = age_entry.get()
            flight_number = flight_number_entry.get()
            destination = destination_entry.get()
            boarding_point = boarding_point_entry.get()
            gender = gender_var.get()

            cursor.execute("SELECT departure_time, arrival_time, available_seats FROM available_flights WHERE flight_number = %s", (flight_number,))
            flight_data = cursor.fetchone()

            if not flight_data:
                messagebox.showwarning("Flight Not Found", "The specified flight number does not exist.")
                return

            departure_time, arrival_time, available_seats = flight_data

            if not all([user_id, first_name, last_name, email, phone, age, flight_number, destination, boarding_point, gender]):
                messagebox.showwarning("Input Error", "Please fill in all fields.")
                return

            # Check if there are available seats
            if int(available_seats) <= 0:
                messagebox.showwarning("No Seats Available", "No seats available for the selected flight.")
                return

            # Allocate seat number 
            seat_number = int(available_seats)

            try:
                # Insert booking details into booked_flights
                cursor.execute("""
                    INSERT INTO booked_flights (user_id, first_name, last_name, email, phone_number, age, flight_number, destination, boarding_point, gender, departure_time, arrival_time, seat_number, booking_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'booked')
                """, (user_id, first_name, last_name, email, phone, age, flight_number, destination, boarding_point, gender, departure_time, arrival_time, seat_number))

                # Update available seats in available_flights
                cursor.execute("UPDATE available_flights SET available_seats = available_seats - 1 WHERE flight_number = %s", (flight_number,))
                connection.commit()

                messagebox.showinfo("Success", f"Flight booked successfully! Your seat number is {seat_number}.")
                booking_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

        booking_window = tk.Toplevel(root)
        booking_window.title("Book Ticket")
        booking_window.geometry("500x750")

        # Create UI elements 
        tk.Label(booking_window, text="User ID:").pack(pady=5)
        user_id_entry = tk.Entry(booking_window)
        user_id_entry.pack(pady=5)

        tk.Label(booking_window, text="First Name:").pack(pady=5)
        first_name_entry = tk.Entry(booking_window)
        first_name_entry.pack(pady=5)

        tk.Label(booking_window, text="Last Name:").pack(pady=5)
        last_name_entry = tk.Entry(booking_window)
        last_name_entry.pack(pady=5)

        tk.Label(booking_window, text="Email:").pack(pady=5)
        email_entry = tk.Entry(booking_window)
        email_entry.pack(pady=5)

        tk.Label(booking_window, text="Phone Number:").pack(pady=5)
        phone_entry = tk.Entry(booking_window)
        phone_entry.pack(pady=5)

        tk.Label(booking_window, text="Age:").pack(pady=5)
        age_entry = tk.Entry(booking_window)
        age_entry.pack(pady=5)

        tk.Label(booking_window, text="Flight Number:").pack(pady=5)
        flight_number_entry = tk.Entry(booking_window)
        flight_number_entry.pack(pady=5)

        tk.Label(booking_window, text="Destination:").pack(pady=5)
        destination_entry = tk.Entry(booking_window)
        destination_entry.pack(pady=5)

        tk.Label(booking_window, text="Boarding Point:").pack(pady=5)
        boarding_point_entry = tk.Entry(booking_window)
        boarding_point_entry.pack(pady=5)

        tk.Label(booking_window, text="Gender:").pack(pady=5)
        gender_var = tk.StringVar()
        tk.Radiobutton(booking_window, text="Male", variable=gender_var, value="Male").pack()
        tk.Radiobutton(booking_window, text="Female", variable=gender_var, value="Female").pack()
        tk.Radiobutton(booking_window, text="Other", variable=gender_var, value="Other").pack()

        tk.Button(booking_window, text="Book Ticket", command=submit_booking).pack(pady=20)




    def generate_ticket_summary():
        booking_id = tk.simpledialog.askstring("Input", "Enter Booking ID:")
        if booking_id:
            try:
                cursor.execute("""
                    SELECT concat(first_name, ' ', last_name), email, flight_number, destination, boarding_point, 
                        status, departure_time, arrival_time, seat_number
                    FROM booked_flights
                    WHERE booking_id = %s
                """, (booking_id,))
                booking = cursor.fetchone()
                if booking:
                    summary_window = tk.Toplevel(root)
                    summary_window.title("Ticket Summary")
                    summary_window.geometry("600x400")

                    tk.Label(summary_window, text="Name: " + str(booking[0]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Email: " + str(booking[1]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Flight Number: " + str(booking[2]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Destination: " + str(booking[3]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Boarding Point: " + str(booking[4]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Status: " + str(booking[5]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Departure Time: " + str(booking[6]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Arrival Time: " + str(booking[7]), font=("Helvetica", 14)).pack(pady=5)
                    tk.Label(summary_window, text="Seat Number: " + str(booking[8]), font=("Helvetica", 14)).pack(pady=5)

                else:
                    messagebox.showwarning("Error", "Booking ID not found.")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")




    def cancel_ticket():
        def submit_cancellation():
            booking_id = booking_id_entry.get()
            if booking_id:
                try:
                    # Retrieve flight number and the number of seats booked
                    cursor.execute("SELECT flight_number FROM booked_flights WHERE booking_id = %s AND status = 'booked'", (booking_id,))
                    booking = cursor.fetchone()
                    
                    if not booking:
                        messagebox.showwarning("Booking Not Found", "The specified booking ID does not exist or is already canceled.")
                        return
                    
                    flight_number = booking[0]

                    # Update available seats 
                    cursor.execute("UPDATE available_flights SET available_seats = available_seats + 1 WHERE flight_number = %s", (flight_number,))
                    
                    # Update booking status 
                    cursor.execute("UPDATE booked_flights SET status = 'canceled' WHERE booking_id = %s", (booking_id,))
                    
                    connection.commit()
                    messagebox.showinfo("Success", "Flight booking canceled successfully!")
                    cancel_window.destroy()
                except mysql.connector.Error as err:
                    messagebox.showerror("Database Error", f"Error: {err}")
            else:
                messagebox.showwarning("Input Error", "Please enter a Booking ID.")

        cancel_window = tk.Toplevel(root)
        cancel_window.title("Cancel Ticket")
        cancel_window.geometry("400x200")

        tk.Label(cancel_window, text="Booking ID:").pack(pady=5)
        booking_id_entry = tk.Entry(cancel_window)
        booking_id_entry.pack(pady=5)

        tk.Button(cancel_window, text="Cancel Ticket", command=submit_cancellation).pack(pady=20)



    show_flights_button = tk.Button(user_frame, text="Show Available Flights", command=show_available_flights, font=("Helvetica", 16), width=30)
    show_flights_button.pack(pady=10)

    book_ticket_button = tk.Button(user_frame, text="Book Ticket", command=book_ticket, font=("Helvetica", 16), width=30)
    book_ticket_button.pack(pady=10)

    cancel_ticket_button = tk.Button(user_frame, text="Cancel Ticket", command=cancel_ticket, font=("Helvetica", 16), width=30)
    cancel_ticket_button.pack(pady=10)

    generate_summary_button = tk.Button(user_frame, text="Generate Ticket", command=generate_ticket_summary, font=("Helvetica", 16), width=30)
    generate_summary_button.pack(pady=10)


    def back_to_main():
        user_frame.pack_forget()
        title_label.pack(pady=20)
        button_frame.pack(pady=50)

    back_button = tk.Button(user_frame, text="Back to Main", command=back_to_main, font=("Helvetica", 16), width=30)
    back_button.pack(pady=20)

def admin_section():
    title_label.pack_forget()
    button_frame.pack_forget()

    admin_frame = tk.Frame(root, bg='skyblue')
    admin_frame.pack(pady=50)

    def show_available_flights():
        try:
            cursor.execute("SELECT * FROM available_flights")
            flights = cursor.fetchall()

            flights_window = tk.Toplevel(root)
            flights_window.title("Available Flights")
            flights_window.geometry("800x500")  # Adjusted size to fit all columns

            columns = (
                'Flight Number', 'Start Location', 'Destination', 
                'Price', 'Departure Time', 'Arrival Time', 
                'Total Seats', 'Available Seats'
            )
            tree = ttk.Treeview(flights_window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100) 

            tree.pack(expand=True, fill='both')

            for flight in flights:
                tree.insert('', tk.END, values=flight)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def add_flight():
        def submit_flight():
            flight_number = flight_number_entry.get()
            start_location = start_location_entry.get()
            destination = destination_entry.get()
            price = price_entry.get()
            departure_time = departure_time_entry.get()
            arrival_time = arrival_time_entry.get()
            total_seats = total_seats_entry.get()

            if not all([flight_number, start_location, destination, price, departure_time, arrival_time, total_seats]):
                messagebox.showwarning("Input Error", "Please fill in all fields.")
                return

            try:
                cursor.execute("""
                    INSERT INTO available_flights (flight_number, start_location, destination, price, departure_time, arrival_time, total_seats, available_seats)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (flight_number, start_location, destination, price, departure_time, arrival_time, total_seats, total_seats))
                connection.commit()
                messagebox.showinfo("Success", "Flight added successfully!")
                add_flight_window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

        add_flight_window = tk.Toplevel(root)
        add_flight_window.title("Add Flight")
        add_flight_window.geometry("500x550") 

        tk.Label(add_flight_window, text="Flight Number:").pack(pady=5)
        flight_number_entry = tk.Entry(add_flight_window)
        flight_number_entry.pack(pady=5)

        tk.Label(add_flight_window, text="Start Location:").pack(pady=5)
        start_location_entry = tk.Entry(add_flight_window)
        start_location_entry.pack(pady=5)

        tk.Label(add_flight_window, text="Destination:").pack(pady=5)
        destination_entry = tk.Entry(add_flight_window)
        destination_entry.pack(pady=5)

        tk.Label(add_flight_window, text="Price:").pack(pady=5)
        price_entry = tk.Entry(add_flight_window)
        price_entry.pack(pady=5)

        tk.Label(add_flight_window, text="Departure Time:").pack(pady=5)
        departure_time_entry = tk.Entry(add_flight_window)
        departure_time_entry.pack(pady=5)

        tk.Label(add_flight_window, text="Arrival Time:").pack(pady=5)
        arrival_time_entry = tk.Entry(add_flight_window)
        arrival_time_entry.pack(pady=5)

        tk.Label(add_flight_window, text="Total Seats:").pack(pady=5)
        total_seats_entry = tk.Entry(add_flight_window)
        total_seats_entry.pack(pady=5)

        tk.Button(add_flight_window, text="Add Flight", command=submit_flight).pack(pady=20)

    def update_flights():
        def select_flight_to_update():
            flight_number = flight_number_entry.get()

            if not flight_number:
                messagebox.showwarning("Input Error", "Please enter a Flight Number to update.")
                return

            try:
                cursor.execute("SELECT * FROM available_flights WHERE flight_number = %s", (flight_number,))
                flight = cursor.fetchone()

                if flight:
                    start_location_entry.delete(0, tk.END)
                    start_location_entry.insert(0, flight[1])

                    destination_entry.delete(0, tk.END)
                    destination_entry.insert(0, flight[2])

                    price_entry.delete(0, tk.END)
                    price_entry.insert(0, flight[3])

                    departure_time_entry.delete(0, tk.END)
                    departure_time_entry.insert(0, flight[4])

                    arrival_time_entry.delete(0, tk.END)
                    arrival_time_entry.insert(0, flight[5])

                    total_seats_entry.delete(0, tk.END)
                    total_seats_entry.insert(0, flight[6])

                else:
                    messagebox.showerror("Error", "No flight found with that number.")

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

        def submit_flight_update():
            flight_number = flight_number_entry.get()
            start_location = start_location_entry.get()
            destination = destination_entry.get()
            price = price_entry.get()
            departure_time = departure_time_entry.get()
            arrival_time = arrival_time_entry.get()
            total_seats = total_seats_entry.get()

            if not all([flight_number, start_location, destination, price, departure_time, arrival_time, total_seats]):
                messagebox.showwarning("Input Error", "Please fill in all fields.")
                return

            try:
                cursor.execute("""
                    UPDATE available_flights
                    SET start_location = %s, destination = %s, price = %s, departure_time = %s, arrival_time = %s, total_seats = %s, available_seats = %s
                    WHERE flight_number = %s
                """, (start_location, destination, price, departure_time, arrival_time, total_seats, total_seats, flight_number))
                connection.commit()
                messagebox.showinfo("Success", "Flight details updated successfully!")
                update_window.destroy()

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

        update_window = tk.Toplevel(root)
        update_window.title("Update Flights")
        update_window.geometry("500x600")

        tk.Label(update_window, text="Enter Flight Number to Update:").pack(pady=5)
        flight_number_entry = tk.Entry(update_window)
        flight_number_entry.pack(pady=5)

        tk.Button(update_window, text="Select Flight", command=select_flight_to_update).pack(pady=10)

        tk.Label(update_window, text="Start Location:").pack(pady=5)
        start_location_entry = tk.Entry(update_window)
        start_location_entry.pack(pady=5)

        tk.Label(update_window, text="Destination:").pack(pady=5)
        destination_entry = tk.Entry(update_window)
        destination_entry.pack(pady=5)

        tk.Label(update_window, text="Price:").pack(pady=5)
        price_entry = tk.Entry(update_window)
        price_entry.pack(pady=5)

        tk.Label(update_window, text="Departure Time:").pack(pady=5)
        departure_time_entry = tk.Entry(update_window)
        departure_time_entry.pack(pady=5)

        tk.Label(update_window, text="Arrival Time:").pack(pady=5)
        arrival_time_entry = tk.Entry(update_window)
        arrival_time_entry.pack(pady=5)

        tk.Label(update_window, text="Total Seats:").pack(pady=5)
        total_seats_entry = tk.Entry(update_window)
        total_seats_entry.pack(pady=5)

        tk.Button(update_window, text="Submit Updates", command=submit_flight_update).pack(pady=20)

    def delete_flight():
        def submit_deletion():
            flight_number = flight_number_entry.get()

            if not flight_number:
                messagebox.showwarning("Input Error", "Please enter a Flight Number to delete.")
                return

            try:
                cursor.execute("DELETE FROM available_flights WHERE flight_number = %s", (flight_number,))
                connection.commit()

                if cursor.rowcount > 0:
                    messagebox.showinfo("Success", "Flight deleted successfully!")
                else:
                    messagebox.showwarning("Not Found", "No flight found with that number.")

                delete_window.destroy()

            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}")

        delete_window = tk.Toplevel(root)
        delete_window.title("Delete Flight")
        delete_window.geometry("400x200")

        tk.Label(delete_window, text="Enter Flight Number to Delete:").pack(pady=5)
        flight_number_entry = tk.Entry(delete_window)
        flight_number_entry.pack(pady=5)

        tk.Button(delete_window, text="Delete Flight", command=submit_deletion).pack(pady=20)

    def display_all_bookings():
        try:
            cursor.execute("SELECT * FROM booked_flights")
            bookings = cursor.fetchall()

            bookings_window = tk.Toplevel(root)
            bookings_window.title("All Bookings")
            bookings_window.geometry("800x500") 


            columns = (
                'Booking ID', 'User ID', 'Flight Number', 'Destination', 
                'Boarding Point', 'Status', 'Booking Date'
            )
            tree = ttk.Treeview(bookings_window, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120) 

            tree.pack(expand=True, fill='both')

            for booking in bookings:
                tree.insert('', tk.END, values=booking)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")



    show_flights_button = tk.Button(admin_frame, text="Show Available Flights", command=show_available_flights, font=("Helvetica", 16), width=30)
    show_flights_button.pack(pady=10)

    add_flights_button = tk.Button(admin_frame, text="Add Flight", command=add_flight, font=("Helvetica", 16), width=30)
    add_flights_button.pack(pady=10)

    update_flights_button = tk.Button(admin_frame, text ="Update Flight",command=update_flights,font=("Helvetica",16), width=30)
    update_flights_button.pack(pady=10)

    delete_flights_button = tk.Button(admin_frame, text ="Delete Flight",command=delete_flight,font=("Helvetica",16), width=30)
    delete_flights_button.pack(pady=10)

    display_bookings_button = tk.Button(admin_frame, text="Display All Bookings", command=display_all_bookings, font=("Helvetica", 16), width=30)
    display_bookings_button.pack(pady=10)

    def back_to_main():
        admin_frame.pack_forget()
        title_label.pack(pady=20)
        button_frame.pack(pady=50)

    back_button = tk.Button(admin_frame, text="Back to Main", command=back_to_main, font=("Helvetica", 16), width=30)
    back_button.pack(pady=20)

def exit_action():
    root.quit()

user_button = tk.Button(button_frame, text="User", command=open_user_section, font=("Helvetica", 16), width=15)
user_button.pack(pady=10)

admin_button = tk.Button(button_frame, text="Admin", command=admin_section, font=("Helvetica", 16), width=15)
admin_button.pack(pady=10)

exit_button = tk.Button(button_frame, text="Exit", command=exit_action, font=("Helvetica", 16), width=15)
exit_button.pack(pady=10)

# Run the main loop 
root.mainloop()
