from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
import io

def get_clickable_elements_and_screenshot(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # Start with maximized window
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
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
        
        # Find all clickable elements
        # clickable_elements = driver.find_elements(By.XPATH, "//*[self::a or self::button or self::input[@type='button'] or self::input[@type='submit']]")
        clickable_elements = driver.find_elements(By.XPATH, """
            //*[
                self::a or
                self::button or
                self::inputx or
                self::select or
                self::textarea or
                self::label or
                self::*[@onclick or @role='button' or @role='link' or @role='menuitem' or @tabindex] or
                self::div[contains(@class, 'button') or contains(@class, 'btn')] or
                self::span[contains(@class, 'button') or contains(@class, 'btn')]
            ]
        """)
        
        elements_info = []
        
        for element in clickable_elements:
            label = element.text.strip() if element.text.strip() else element.get_attribute("value")
            if not label:
                label = element.get_attribute("aria-label") or element.get_attribute("title") or "No label"
            
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
            if coordinates['x2'] > 0 and coordinates['y2'] > 0 and coordinates['x1'] < viewport_metrics['width'] and coordinates['y1'] < viewport_metrics['height']:
                elements_info.append({
                    "label": label,
                    "coordinates": coordinates
                })
        
        return elements_info, screenshot, viewport_metrics
    
    finally:
        driver.quit()

def draw_bounding_boxes(screenshot, elements_info, viewport_metrics):
    image = Image.open(io.BytesIO(screenshot))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except IOError:
        font = ImageFont.load_default()
    
    dpr = viewport_metrics['devicePixelRatio']
    
    for element in elements_info:
        coords = element['coordinates']
        label = element['label']
        
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
    
    return image

# Example usage
url = "https://shopee.sg"
elements_info, screenshot, viewport_metrics = get_clickable_elements_and_screenshot(url)

# Draw bounding boxes on the screenshot
annotated_image = draw_bounding_boxes(screenshot, elements_info, viewport_metrics)

# Save the annotated image
annotated_image.save("annotated_screenshot.png")

print(f"Screenshot with bounding boxes saved as 'annotated_screenshot.png'")
print(f"Viewport dimensions: {viewport_metrics['width']}x{viewport_metrics['height']}")
print(f"Device Pixel Ratio: {viewport_metrics['devicePixelRatio']}")

# Print element information
for element in elements_info:
    print(f"Label: {element['label']}")
    print(f"Coordinates: {element['coordinates']}")
    print("---")