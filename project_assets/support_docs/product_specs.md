# E-Shop Checkout - Product Specifications

## Version: 1.0
## Last Updated: November 2024

---

## 1. Product Catalog

### 1.1 Available Products
The checkout page displays three products:

| Product ID | Product Name | Price | Category |
|------------|--------------|-------|----------|
| PROD-001 | Premium Laptop | $999.99 | Electronics |
| PROD-002 | Wireless Headphones | $199.99 | Audio |
| PROD-003 | Mechanical Keyboard | $149.99 | Peripherals |

### 1.2 Product Display Requirements
- Each product must display: emoji icon, name, price, and "Add to Cart" button
- Product prices are inclusive of taxes
- All prices displayed in USD with two decimal places
- Products should be displayed in a responsive grid layout

---

## 2. Shopping Cart Functionality

### 2.1 Add to Cart Behavior
- When a user clicks "Add to Cart", the item is added to the cart section
- If the item already exists in cart, increment quantity by 1
- Cart must display: product name, quantity selector, item total, and remove button
- Cart persists in browser session (page state only, no backend persistence)

### 2.2 Quantity Management
- Minimum quantity per item: 1
- Maximum quantity per item: No limit (unrestricted)
- Quantity can be modified using the quantity input field in cart
- Changing quantity updates the item total and cart total immediately
- Setting quantity to 0 or negative values should be prevented by input validation

### 2.3 Remove from Cart
- Each cart item has a "Remove" button
- Clicking remove completely removes the item from cart
- If cart becomes empty after removal, display "Your cart is empty. Add some products!"

---

## 3. Discount Code System

### 3.1 Valid Discount Codes
The system supports the following discount codes:

| Code | Discount | Description |
|------|----------|-------------|
| SAVE15 | 15% | Standard discount for returning customers |
| WELCOME10 | 10% | First-time customer welcome discount |
| SUMMER20 | 20% | Seasonal promotion (summer special) |

### 3.2 Discount Application Rules
- Discount codes are **case-insensitive** (SAVE15, save15, Save15 all work)
- Only **one discount code** can be applied per order
- Discount applies to the **subtotal only** (before shipping)
- Discount does **not apply to shipping costs**
- Invalid codes display error message: "✗ Invalid discount code"
- Valid codes display success message: "✓ Discount code "{CODE}" applied! You save {X}%"

### 3.3 Discount Calculation Formula
```
Subtotal = Sum of (Product Price × Quantity) for all items
Discount Amount = Subtotal × (Discount Percentage / 100)
Subtotal After Discount = Subtotal - Discount Amount
Total = Subtotal After Discount + Shipping Cost
```

### 3.4 Discount Display Requirements
- When discount is applied, show discount breakdown in cart total section
- Display format: "Discount (X%): -$Y.YY" in red text
- Discount amount should be shown as negative value

---

## 4. Shipping Options

### 4.1 Available Shipping Methods

#### Standard Shipping
- **Cost:** FREE ($0.00)
- **Delivery Time:** 5-7 business days
- **Default Selection:** Yes (pre-selected)
- **Availability:** All locations

#### Express Shipping
- **Cost:** $10.00 (flat rate)
- **Delivery Time:** 1-2 business days
- **Availability:** All locations
- **Additional Info:** Guaranteed delivery or money back

### 4.2 Shipping Calculation Rules
- Shipping cost is added to the order total after discount application
- Shipping method can be changed at any time before payment
- Changing shipping method updates total price immediately
- No shipping is charged if cart is empty

---

## 5. Order Total Calculation

### 5.1 Price Breakdown Components
1. **Subtotal:** Sum of all cart items (price × quantity)
2. **Discount:** Percentage reduction on subtotal (if code applied)
3. **Shipping:** Based on selected shipping method
4. **Total:** Final amount to be charged

### 5.2 Calculation Order
```
Step 1: Calculate Subtotal
Step 2: Apply Discount (if applicable)
Step 3: Add Shipping Cost
Step 4: Display Total
```

### 5.3 Display Requirements
- All amounts must display currency symbol ($) and two decimal places
- Subtotal, Discount (if applicable), Shipping, and Total must be clearly labeled
- Total should be prominently displayed in larger, bold font
- All calculations update in real-time when cart or selections change

---

## 6. Payment Processing

### 6.1 Supported Payment Methods

#### Credit Card
- **Supported Cards:** Visa, MasterCard, American Express
- **Default Selection:** Yes (pre-selected)
- **Processing:** Immediate
- **Description:** "Pay securely with your credit card"

#### PayPal
- **Processing:** Redirect to PayPal
- **Description:** "Pay securely with your PayPal account"
- **Integration:** Mock implementation (no actual PayPal redirect in this version)

### 6.2 Payment Submission
- Payment is triggered by clicking "Pay Now" button
- Button is green color (#4CAF50) as per UI guidelines
- Button spans full width of form section
- On successful validation, display success message
- Success message: "✅ Payment Successful! Thank you for your order."

---

## 7. Business Rules Summary

### 7.1 Order Prerequisites
- Cart must contain at least one item to proceed with payment
- All required form fields must be valid
- User must select shipping method (default: Standard)
- User must select payment method (default: Credit Card)

### 7.2 Price Integrity
- Product prices are fixed and cannot be modified by client
- Discount codes follow strict validation rules
- Shipping costs are fixed based on selected method
- All calculations are performed client-side for this demo version

### 7.3 Session Behavior
- Cart state persists during browser session only
- Refreshing page resets all data (no backend persistence)
- No user authentication required for this version
- No order history or tracking in this version

---

## 8. Error Handling

### 8.1 Cart Validation
- Prevent checkout with empty cart
- Alert message: "Your cart is empty! Please add items before checking out."

### 8.2 Discount Code Validation
- Invalid code displays inline error message
- Error is dismissible by entering a new code
- Previous discount is removed when invalid code is entered

### 8.3 Form Validation
- All validation errors display in red text below respective fields
- Multiple errors can be displayed simultaneously
- Form cannot be submitted until all validations pass

---

## 9. Technical Notes

### 9.1 Client-Side Implementation
- All functionality implemented in vanilla JavaScript
- No external libraries or frameworks required
- No backend API calls in this version
- All calculations and validations happen client-side

### 9.2 Browser Compatibility
- Designed for modern browsers (Chrome, Firefox, Safari, Edge)
- Responsive design for mobile and desktop
- Minimum supported resolution: 320px width

### 9.3 Performance Requirements
- Cart updates should be instantaneous (< 100ms)
- Form validation should provide immediate feedback
- Page should load completely within 3 seconds on standard connection

---

**End of Product Specifications**
