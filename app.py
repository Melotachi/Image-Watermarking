import os
from tkinter import *
from tkinter import filedialog as fd
from PIL import Image, ImageTk, ImageDraw, ImageFont

class Application(Tk):
    
    def __init__(self):
        super().__init__()
        self.minsize(1024, 768)
        self.config(bg="#1A3636")
        self.title('Image & Watermark')

        # Create a Canvas for scrolling
        self.canvas = Canvas(self, bg="#1A3636")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        # Create a Scrollbar and attach it to the Canvas
        self.scroll_y = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=RIGHT, fill=Y)

        # Create a Frame to contain the images and place it on the Canvas
        self.scrollable_frame = Frame(self.canvas, bg="#1A3636")
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        # Initialize the Add New Photos button
        self.add_button = Button(text='Add New Photos', activebackground='#F8EDE3',
                                 anchor='center', justify='center', padx=10, pady=5, width=10, height=1, command=self.add_button) 
        self.add_button.pack(side=TOP, pady=20)

        self.images = []  # Store PhotoImage objects
        self.file_paths = []  # Store file paths
        self.image_list = []  # Store references to images to prevent garbage collection
        self.ALLOWED_EXTENSIONS = ["jpg", "png"] # You can add more extensions if you want
        self.MAX_WIDTH = 270 # Maximum width of the image (You can change it if you want)
        self.MAX_HEIGHT = 360 # Maximum height of the image (You can change it if you want)
        self.WATERMARK_TEXT = "Watermark" # Watermark text (You can change it if you want)
        
        self.show_photos()
        
        self.mainloop()
    
    def add_button(self):
        files = fd.askopenfilenames(parent=self, title='Add New Photos')
        for file in files:
            file_name = os.path.basename(file)
            extension = file_name.split('.')[-1]
            if extension in self.ALLOWED_EXTENSIONS:
                # Resize image and create PhotoImage object
                img = Image.open(file)
                img.thumbnail((self.MAX_WIDTH, self.MAX_HEIGHT))  # Resize image to fit within max dimensions
                photo = ImageTk.PhotoImage(img)
                
                self.images.append(photo)
                self.file_paths.append(file)  # Save the file path
        self.show_photos()
    
    def show_photos(self):
        # Clear existing photo frames
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Display all images
        for i, image in enumerate(self.images):
            image_frame = Frame(self.scrollable_frame, width=300, height=400, padx=20, pady=30, bg="#1A3636")
            image_frame.grid(row=1 + (i // 4), column=i % 4, padx=20, pady=20)

            image_name = Label(image_frame, text=os.path.basename(self.file_paths[i].split('.')[0]), anchor='center', justify='center', fg="#A28B55", font=("Arial", 16, 'bold'), bg="#1A3636")
            image_name.grid(row=0, column=0, columnspan=2)

            # Create a Button with the image as its content
            image_button = Button(image_frame, image=image, command=lambda i=i: self.image_click(i))
            image_button.grid(row=1, column=0, columnspan=2)

            delete_button = Button(image_frame, text='Delete', anchor='center', justify='center', width=10, height=1,
                                   command=lambda i=i: self.delete_button(i))
            delete_button.grid(row=2, column=0, padx=15, pady=15)

            download_button = Button(image_frame, text='Download', anchor='center', justify='center', width=10, height=1,
                                     command=lambda i=i: self.download_button(i))
            download_button.grid(row=2, column=1, padx=15, pady=15)

            # Store reference to image in `self.image_list` to prevent garbage collection
            self.image_list.append(image)
                
    def delete_button(self, index):
        # Remove image and its file path
        if 0 <= index < len(self.images):
            del self.images[index]
            # os.remove(self.file_paths[index])  # Uncomment to remove the file from the filesystem
            del self.file_paths[index]  # Remove the file path
            self.show_photos()  # Refresh the photo display
    
    def download_button(self, index):
        if 0 <= index < len(self.file_paths):
            # Ask user for save location and file type
            save_path = fd.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            
            if save_path:
                # Check the file extension and save the image accordingly
                file_extension = os.path.splitext(save_path)[1].lower()
                img = Image.open(self.file_paths[index])
                
                # Add watermark to the image
                img_with_watermark = self.add_watermark(img)
                
                # Save the image with the selected file extension
                if file_extension == ".jpg":
                    img_with_watermark.convert("RGB").save(save_path, "JPEG")
                elif file_extension == ".png":
                    img_with_watermark.save(save_path, "PNG")
                else:
                    print(f"Unsupported file format: {file_extension}")

                print(f'Saved {save_path}')

    
    def image_click(self, index):
        if 0 <= index < len(self.file_paths):
            # Create a new Toplevel window
            top = Toplevel(self)
            top.title("Full Size Image")
            
            # Open the full-size image
            img = Image.open(self.file_paths[index])
            img_width, img_height = img.size
            
            # Create a PhotoImage object
            photo = ImageTk.PhotoImage(img)
            
            # Create a Label widget to display the image
            label = Label(top, image=photo)
            label.pack()
            
            # Store reference to image in `self.image_list` to prevent garbage collection
            self.image_list.append(photo)
            
            # Set the size of the Toplevel window to the size of the image
            top.geometry(f"{img_width}x{img_height}")

    def add_watermark(self, img): # You can also add a watermark to the different part of the image, I just added it to the bottom right corner of the image
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        width, height = img.size
        watermark_text = self.WATERMARK_TEXT
        
        # Choose a font and size
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), watermark_text, font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        position = (width - text_width - 10, height - text_height - 10)
        
        # Draw text on the image with RGB color
        draw.text(position, watermark_text, font=font, fill=(255, 165, 0))  # White color without transparency
        
        return img

