# E-Shop Checkout - Business Rules and Validation

## Document Version: 1.0
## Last Updated: November 2024
## Purpose: Define business logic, validation rules, and edge cases

---

## 1. Form Validation Rules

### 1.1 Name Field Validation
**Field ID:** `name`
**Field Type:** Text input
**Required:** Yes

**Validation Rules:**
- Must not be empty
- Minimum length: 2 characters
- Maximum length: 100 characters
- Should contain only letters and spaces (a-z, A-Z, and space)
- Leading/trailing spaces should be trimmed before validation

**Error Messages:**
- Empty field: "Name is required"
- Too short: "Name must be at least 2 characters"
- Invalid characters: "Name should contain only letters and spaces"

**Valid Examples:**
- "John Doe"
- "Mary Jane Smith"
- "José García"

**Invalid Examples:**
- "" (empty)
- "J" (too short)
- "John123" (contains numbers)
- "   " (only spaces)

---

### 1.2 Email Field Validation
**Field ID:** `email`
**Field Type:** Email input
**Required:** Yes

**Validation Rules:**
- Must not be empty
- Must follow standard email format: `local@domain.extension`
- Must contain exactly one @ symbol
- Domain must have at least one dot
- No spaces allowed
- Case-insensitive

**Regular Expression Pattern:**
```regex
^[^\s@]+@[^\s@]+\.[^\s@]+$
```

**Error Messages:**
- Empty field: "Please enter a valid email address"
- Invalid format: "Please enter a valid email address"

**Valid Examples:**
- "john.doe@example.com"
- "user+tag@domain.co.uk"
- "test_email@subdomain.example.com"
- "NAME@EXAMPLE.COM" (case doesn't matter)

**Invalid Examples:**
- "" (empty)
- "notanemail" (no @ symbol)
- "@example.com" (no local part)
- "user@" (no domain)
- "user @example.com" (contains space)
- "user@@example.com" (multiple @ symbols)

---

### 1.3 Phone Field Validation
**Field ID:** `phone`
**Field Type:** Tel input
**Required:** No (optional field)

**Validation Rules:**
- Can be empty (optional)
- If provided, should be a valid phone format
- Allowed characters: digits (0-9), spaces, hyphens (-), parentheses (), plus sign (+)
- Minimum length (excluding formatting): 10 digits
- Maximum length: 20 characters

**Error Messages:**
- Invalid format: "Please enter a valid phone number"

**Valid Examples:**
- "+1 (555) 123-4567"
- "555-123-4567"
- "+44 20 7123 4567"
- "5551234567"
- "" (empty is valid since it's optional)

**Invalid Examples:**
- "123" (too short)
- "abc-def-ghij" (contains letters)
- "555 123 4567 ext 890" (contains invalid text)

---

### 1.4 Address Field Validation
**Field ID:** `address`
**Field Type:** Textarea
**Required:** Yes

**Validation Rules:**
- Must not be empty
- Minimum length: 10 characters
- Maximum length: 500 characters
- Should include street address at minimum
- Leading/trailing spaces should be trimmed

**Error Messages:**
- Empty field: "Address is required"
- Too short: "Address must be at least 10 characters"

**Valid Examples:**
- "123 Main St, Apt 4B, New York, NY 10001"
- "42 Wallaby Way, Sydney, NSW 2000, Australia"
- "1600 Pennsylvania Avenue NW, Washington, DC 20500"

**Invalid Examples:**
- "" (empty)
- "Main St" (too short)
- "   " (only spaces)

---

## 2. Shipping Method Business Rules

### 2.1 Standard Shipping
**Value:** `standard`
**Cost:** $0.00 (FREE)
**Delivery Time:** 5-7 business days

**Business Rules:**
- Default selection (pre-selected when page loads)
- Available for all products
- No minimum order value required
- Delivery time is estimate only, not guaranteed
- Business days exclude weekends and holidays

**Use Cases:**
- Customer not in a hurry
- Cost-conscious customers
- Default option for all orders

---

### 2.2 Express Shipping
**Value:** `express`
**Cost:** $10.00 (flat rate)
**Delivery Time:** 1-2 business days

**Business Rules:**
- Available for all products
- Flat rate regardless of cart value or weight
- Guaranteed delivery or money back
- Orders placed before 2 PM EST ship same day
- Orders after 2 PM EST ship next business day
- Business days exclude weekends and holidays

**Use Cases:**
- Urgent orders
- Customer willing to pay for speed
- Gift orders with tight deadlines

---

## 3. Payment Method Business Rules

### 3.1 Credit Card
**Value:** `credit-card`
**Supported Cards:** Visa, MasterCard, American Express

**Business Rules:**
- Default selection (pre-selected when page loads)
- Immediate payment processing
- Secure payment gateway (PCI compliant)
- 3D Secure authentication for eligible cards
- Payment is charged immediately upon order submission

**Processing Time:**
- Authorization: Instant
- Funds capture: Immediate
- Refund processing: 5-7 business days

---

### 3.2 PayPal
**Value:** `paypal`
**Description:** Pay securely with your PayPal account

**Business Rules:**
- Redirects to PayPal for authentication
- Supports PayPal balance, linked bank accounts, and cards
- Payment is processed through PayPal's secure platform
- Customer must have PayPal account or can create one during checkout
- Order is confirmed only after successful PayPal payment

**Processing Time:**
- Authorization: Instant (via PayPal)
- Funds capture: Immediate
- Refund processing: 3-5 business days

---

## 4. Order Submission Rules

### 4.1 Prerequisites for Order Submission
All of the following conditions must be met:

1. **Cart Requirements:**
   - Cart must contain at least one item
   - All cart items must be in stock (always true in current version)
   - Cart quantities must be positive integers

2. **Form Validation:**
   - Name field must be valid and not empty
   - Email field must be valid and not empty
   - Address field must be valid and not empty
   - Phone field, if provided, must be valid (optional)

3. **Selection Requirements:**
   - Shipping method must be selected (default: standard)
   - Payment method must be selected (default: credit-card)

4. **UI State:**
   - No validation errors displayed
   - Form is not already being submitted (prevent double submission)

---

### 4.2 Order Submission Process

**Step 1: Client-Side Validation**
- Validate all form fields
- Check cart is not empty
- Display errors if validation fails
- Prevent form submission if validation fails

**Step 2: Payment Processing (Simulated)**
- In current version, this is simulated client-side
- In production, would call backend payment API
- If payment fails, display error and allow retry

**Step 3: Success Confirmation**
- Hide checkout form
- Display success message: "✅ Payment Successful! Thank you for your order."
- Scroll to success message
- In production, would also:
  - Send confirmation email
  - Generate order number
  - Clear cart
  - Redirect to order confirmation page

---

## 5. Discount Code Business Rules

### 5.1 Valid Discount Codes

| Code | Discount | Type | Restrictions |
|------|----------|------|--------------|
| SAVE15 | 15% off | Percentage | No minimum order |
| WELCOME10 | 10% off | Percentage | First-time customers (not enforced in current version) |
| SUMMER20 | 20% off | Percentage | Seasonal offer |

---

### 5.2 Discount Application Rules

**Rule 1: Case Insensitivity**
- Discount codes are case-insensitive
- "SAVE15", "save15", "Save15", "sAvE15" all work

**Rule 2: Single Discount Only**
- Only one discount code can be applied per order
- Applying a new code replaces the previous code
- To remove a discount, customer must enter an invalid code or refresh page

**Rule 3: Application Scope**
- Discount applies to subtotal only
- Discount does NOT apply to shipping costs
- Discount is calculated before shipping is added

**Rule 4: Validation**
- Invalid codes display error immediately
- Valid codes display success message immediately
- Discount is applied to cart total instantly

**Rule 5: Persistence**
- Discount code persists while user is on the page
- Discount is recalculated if cart items change
- Discount is lost if page is refreshed (no backend in current version)

---

### 5.3 Discount Calculation Examples

**Example 1: Basic Discount**
```
Subtotal: $1000.00
Discount Code: SAVE15 (15%)
Discount Amount: $1000.00 × 15% = $150.00
Subtotal After Discount: $1000.00 - $150.00 = $850.00
Shipping: $10.00 (Express)
Total: $850.00 + $10.00 = $860.00
```

**Example 2: Discount with Free Shipping**
```
Subtotal: $500.00
Discount Code: SUMMER20 (20%)
Discount Amount: $500.00 × 20% = $100.00
Subtotal After Discount: $500.00 - $100.00 = $400.00
Shipping: $0.00 (Standard - Free)
Total: $400.00 + $0.00 = $400.00
```

**Example 3: Discount Does NOT Apply to Shipping**
```
Subtotal: $100.00
Discount Code: WELCOME10 (10%)
Discount Amount: $100.00 × 10% = $10.00
Subtotal After Discount: $100.00 - $10.00 = $90.00
Shipping: $10.00 (Express)
❌ WRONG: Discount on total including shipping
Total: $90.00 + $10.00 = $100.00
✅ CORRECT: Discount on subtotal only
```

---

## 6. Cart Management Rules

### 6.1 Adding Items to Cart
- Clicking "Add to Cart" adds one unit of the product
- If product already in cart, increment quantity by 1
- No maximum quantity limit per item
- No maximum number of different items
- Cart updates immediately with visual feedback

---

### 6.2 Modifying Cart Quantities
- Quantity can be changed using the input field in cart
- Minimum quantity: 1
- Maximum quantity: No limit
- Setting quantity to 0 should not be allowed (minimum is 1)
- Setting quantity to negative should not be allowed
- Non-integer quantities should be rounded or rejected
- Price recalculates immediately upon quantity change

---

### 6.3 Removing Items from Cart
- Each item has a "Remove" button
- Clicking "Remove" deletes the item completely from cart
- No confirmation dialog (immediate removal)
- If cart becomes empty, show empty cart message
- All totals update immediately after removal

---

### 6.4 Empty Cart Behavior
- Display message: "Your cart is empty. Add some products!"
- All totals show $0.00
- Discount section remains visible
- Checkout form remains visible
- Attempting to submit order shows alert: "Your cart is empty! Please add items before checking out."

---

## 7. Price Calculation Rules

### 7.1 Order of Operations (CRITICAL)
This order must be strictly followed:

```
1. Calculate Subtotal
   Subtotal = Σ (Product Price × Quantity) for all items

2. Apply Discount (if valid code entered)
   Discount Amount = Subtotal × (Discount Percentage ÷ 100)
   Subtotal After Discount = Subtotal - Discount Amount

3. Add Shipping Cost
   Shipping Cost = $0.00 (Standard) or $10.00 (Express)

4. Calculate Total
   Total = Subtotal After Discount + Shipping Cost
```

**Example Calculation:**
```
Cart Items:
- Premium Laptop: $999.99 × 1 = $999.99
- Wireless Headphones: $199.99 × 2 = $399.98

Step 1: Subtotal = $999.99 + $399.98 = $1,399.97

Step 2: Discount (SAVE15 = 15%)
        Discount Amount = $1,399.97 × 0.15 = $209.9955 ≈ $210.00
        Subtotal After Discount = $1,399.97 - $210.00 = $1,189.97

Step 3: Shipping (Express) = $10.00

Step 4: Total = $1,189.97 + $10.00 = $1,199.97
```

---

### 7.2 Rounding Rules
- All prices stored and calculated with 2 decimal places
- Intermediate calculations may have more precision
- Final displayed amounts always round to 2 decimal places
- Rounding method: Round half up (standard rounding)
  - Example: $10.125 → $10.13
  - Example: $10.124 → $10.12

---

## 8. Edge Cases and Special Scenarios

### 8.1 Empty Cart Checkout Attempt
**Scenario:** User tries to pay with empty cart
**Expected Behavior:**
- Alert message: "Your cart is empty! Please add items before checking out."
- Form validation fails
- Order is not submitted
- Form remains visible

---

### 8.2 Invalid Email Format
**Scenario:** User enters invalid email
**Expected Behavior:**
- Red border around email field
- Error message below field: "Please enter a valid email address"
- Form submission prevented
- Other fields may still have errors

---

### 8.3 Multiple Validation Errors
**Scenario:** User submits form with multiple empty/invalid fields
**Expected Behavior:**
- All invalid fields show red border
- All relevant error messages displayed simultaneously
- Form submission prevented
- User can fix errors in any order
- Errors disappear as user corrects each field

---

### 8.4 Discount Code Changes After Cart Update
**Scenario:** User has discount applied, then adds/removes items
**Expected Behavior:**
- Discount percentage remains the same
- Discount amount recalculates based on new subtotal
- Discount code remains valid
- Total updates immediately

---

### 8.5 Shipping Method Change
**Scenario:** User changes from Standard to Express or vice versa
**Expected Behavior:**
- Shipping cost updates immediately
- Total price recalculates
- Visual indication of selected method (green border)
- Previous selection deselected

---

### 8.6 Real-time Validation
**Scenario:** User types in form field
**Expected Behavior:**
- If field was showing error, error clears as user types
- Field border returns to normal
- Error message disappears
- Validation re-runs on form submission

---

## 9. Success State Rules

### 9.1 Successful Order Completion
**Conditions Required:**
- All validations passed
- Cart contains items
- Payment processed successfully (simulated)

**Actions Taken:**
1. Hide checkout form (`display: none`)
2. Show success message (`display: block`)
3. Success message displays: "✅ Payment Successful! Thank you for your order."
4. Smooth scroll to success message
5. In production: send email, clear cart, generate order ID

---

### 9.2 Success Message Display
**Visual Requirements:**
- Background: Light green (#d4edda)
- Text: Dark green (#155724)
- Border: Green (#c3e6cb)
- Padding: 20px
- Center aligned
- Font size: 20px
- Font weight: bold
- Contains checkmark emoji: ✅

---

## 10. Data Integrity Rules

### 10.1 Product Prices
- Product prices are hardcoded and immutable
- Prices cannot be modified via client-side code
- In production, prices would be validated server-side
- All price changes require code update

---

### 10.2 Discount Codes
- Valid codes are defined in code
- Cannot be generated or modified client-side
- In production, would be validated server-side
- Codes are alphanumeric only

---

### 10.3 Calculation Integrity
- All calculations performed client-side for demo
- In production, critical calculations (total, discount) must be verified server-side
- Client-side calculations for user experience only
- Server-side calculations are source of truth

---

## 11. Testing Considerations

### 11.1 Positive Test Scenarios
1. Add items to cart successfully
2. Apply valid discount code
3. Change shipping methods
4. Change payment methods
5. Submit valid form with all required fields
6. Modify cart quantities
7. Remove items from cart

---

### 11.2 Negative Test Scenarios
1. Submit form with empty required fields
2. Submit form with invalid email
3. Apply invalid discount code
4. Try to checkout with empty cart
5. Enter invalid phone format
6. Enter address too short

---

### 11.3 Boundary Test Scenarios
1. Name with exactly 2 characters (minimum)
2. Address with exactly 10 characters (minimum)
3. Very large quantity numbers
4. Multiple items with maximum quantities

---

**End of Business Rules Document**
