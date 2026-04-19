import cv2
import os

# --- CONFIGURATION ---
SOURCE_IMAGE = 'gurgaon-map-watermark.jpg' 
OUTPUT_FILE = 'sector_logic.csv'
# ---------------------

# Create CSV header if file doesn't exist
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, 'w') as f:
        f.write("sector,x_pct,y_pct,landmark\n")

def click_event(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Calculate percentage coordinates (Resolution Independent)
        h, w = img.shape[:2]
        x_pct = round(x / w, 4)
        y_pct = round(y / h, 4)
        
        print(f"\n--- New Data Point at {x_pct}, {y_pct} ---")
        sector_num = input("Enter Sector Number: ")
        landmark = input("Enter Landmark (or press Enter to skip): ")
        
        # Append to CSV
        with open(OUTPUT_FILE, 'a') as f:
            f.write(f"{sector_num},{x_pct},{y_pct},{landmark}\n")
        
        # Visual feedback on the picker tool
        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)
        cv2.putText(img, str(sector_num), (x + 10, y + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.imshow('Gurgaon Data Picker', img)
        print(f"Saved: Sector {sector_num}")

# Load image
img = cv2.imread(SOURCE_IMAGE)
if img is None:
    print(f"Error: Could not find {SOURCE_IMAGE}. Check the filename!")
else:
    cv2.imshow('Gurgaon Data Picker', img)
    cv2.setMouseCallback('Gurgaon Data Picker', click_event)
    print("INSTRUCTIONS:")
    print("1. Click the center of a sector on the map.")
    print("2. Go to your terminal/VS Code console and type the Sector Number.")
    print("3. Press 'q' on your keyboard to save and close when finished.")
    
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()