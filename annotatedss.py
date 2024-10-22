from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from PIL import Image, ImageDraw, ImageFont
import io
import time

def get_interactive_elements_and_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Wait for the page to stabilize
        time.sleep(2)
        
        # Get viewport dimensions and scroll position
        viewport_metrics = driver.execute_script("""
            return {
                width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
                height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight,
                scrollX: window.pageXOffset,
                scrollY: window.pageYOffset,
                devicePixelRatio: window.devicePixelRatio || 1
            };
        """)
        
        # Capture visible part of the page
        screenshot = driver.get_screenshot_as_png()
        
        # Find all potentially interactive elements
        interactive_elements = driver.find_elements(By.XPATH, """
            //*[
                self::a or
                self::button or
                self::input or
                self::select or
                self::textarea or
                self::label or
                self::*[@onclick or @role='button' or @role='link' or @role='menuitem' or @role='slider' or
                        @role='scrollbar' or @role='checkbox' or @role='radio' or @role='textbox' or
                        @role='combobox' or @role='listbox' or @role='switch' or @tabindex or
                        contains(@class, 'button') or contains(@class, 'btn') or
                        contains(@class, 'dropdown') or contains(@class, 'menu-item') or
                        contains(@class, 'clickable') or contains(@class, 'selectable')]
            ]
        """)
        
        elements_info = []
        
        for element in interactive_elements:
            try:
                label = element.text.strip() if element.text.strip() else element.get_attribute("value")
                if not label:
                    label = (element.get_attribute("aria-label") or 
                             element.get_attribute("placeholder") or
                             element.get_attribute("title") or 
                             element.get_attribute("name") or 
                             element.get_attribute("id") or 
                             "No label")
                
                # Get element's position relative to the viewport
                rect = driver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    return {
                        top: rect.top,
                        left: rect.left,
                        width: rect.width,
                        height: rect.height
                    };
                """, element)
                
                # Calculate coordinates relative to the viewport
                coordinates = {
                    "x1": max(0, rect['left']),
                    "y1": max(0, rect['top']),
                    "x2": min(viewport_metrics['width'], rect['left'] + rect['width']),
                    "y2": min(viewport_metrics['height'], rect['top'] + rect['height'])
                }
                
                # Only add elements that are at least partially visible in the viewport
                if (coordinates['x2'] > 0 and coordinates['y2'] > 0 and
                    coordinates['x1'] < viewport_metrics['width'] and coordinates['y1'] < viewport_metrics['height'] and
                    rect['width'] > 0 and rect['height'] > 0):
                    elements_info.append({
                        "label": label,
                        "coordinates": coordinates,
                        "tag_name": element.tag_name,
                        "type": element.get_attribute("type"),
                        "role": element.get_attribute("role")
                    })
            except (StaleElementReferenceException, TimeoutException) as e:
                print(f"Error processing element: {e}")
                continue  # Skip this element and continue with the next one
        
        return elements_info, screenshot, viewport_metrics
    
    finally:
        driver.quit()

import io
import os
from PIL import Image, ImageDraw, ImageFont

def draw_bounding_boxes(screenshot, elements_info, viewport_metrics):
    image = Image.open(io.BytesIO(screenshot))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
    
    dpr = viewport_metrics['devicePixelRatio']
    image_width, image_height = image.size
    
    yolo_annotations = []
    
    for element in elements_info:
        coords = element['coordinates']
        label = f"{element['tag_name']}:{element['type'] or element['role'] or ''} - {element['label']}"
        
        # Scale coordinates for high DPI displays
        scaled_coords = [
            coords['x1'] * dpr,
            coords['y1'] * dpr,
            coords['x2'] * dpr,
            coords['y2'] * dpr
        ]
        
        draw.rectangle(scaled_coords, outline="red", width=2)
        
        # Adjust label position to be inside the box if possible
        label_x = scaled_coords[0]
        label_y = max(scaled_coords[1] - 15 * dpr, 0)  # Place above the box, but not off the image
        
        # Draw a semi-transparent background for the label
        text_bbox = draw.textbbox((label_x, label_y), label, font=font)
        draw.rectangle(text_bbox, fill=(255, 0, 0, 128))  # Semi-transparent red
        
        draw.text((label_x, label_y), label, fill="white", font=font)
        
        # Calculate YOLO format annotations
        x_center = (scaled_coords[0] + scaled_coords[2]) / 2 / image_width
        y_center = (scaled_coords[1] + scaled_coords[3]) / 2 / image_height
        width = (scaled_coords[2] - scaled_coords[0]) / image_width
        height = (scaled_coords[3] - scaled_coords[1]) / image_height
        
        # Assign a class number (you may want to modify this based on your specific classes)
        class_number = 0  # Default class
        if 'button' in element['tag_name'].lower() or 'btn' in element.get('class', '').lower():
            class_number = 1
        elif element['tag_name'].lower() == 'a':
            class_number = 2
        # Add more class assignments as needed
        
        yolo_annotations.append(f"{class_number} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    # Generate a unique filename for YOLO annotations
    base_filename = "yolo_annotations"
    counter = 0
    while os.path.exists(f"{base_filename}_{counter}.txt"):
        counter += 1
    output_file = f"{base_filename}_{counter}.txt"
    
    # Write YOLO annotations to file
    with open(output_file, 'w') as f:
        f.write('\n'.join(yolo_annotations))
    
    print(f"YOLO annotations saved as '{output_file}'")
    
    return image

# Example usage
url = "https://www.linkedin.com/in/yashchopra1411/"
elements_info, screenshot, viewport_metrics = get_interactive_elements_and_screenshot(url)

# Draw bounding boxes on the screenshot
annotated_image = draw_bounding_boxes(screenshot, elements_info, viewport_metrics)

# Save the annotated image
annotated_image.save("annotated_screenshot1.png")

print(f"Screenshot with bounding boxes saved as 'annotated_screenshot.png'")
print(f"Viewport dimensions: {viewport_metrics['width']}x{viewport_metrics['height']}")
print(f"Device Pixel Ratio: {viewport_metrics['devicePixelRatio']}")

# Print element information
for element in elements_info:
    print(f"Tag: {element['tag_name']}")
    print(f"Type/Role: {element['type'] or element['role'] or 'N/A'}")
    print(f"Label: {element['label']}")
    print(f"Coordinates: {element['coordinates']}")
    print("---")