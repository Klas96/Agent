# Token System Deprecation - Donation-Only Migration Plan

## 🎯 **Overview**

This plan outlines the migration from a token-based system to a simplified donation-only model. The goal is to remove complexity while maintaining the core functionality.

## 📋 **Current System Analysis**

### **Token System Components to Remove:**

1. **Flow Types**:
   - `TOKENED_USER` → Remove
   - `TOKENLESS_USER` → Remove  
   - `PAYMENT_PENDING` → Remove
   - New: `DONATION_USER` (single flow type)

2. **Token Management**:
   - `TokenValidationNode` → Remove
   - `TokenConsumptionNode` → Remove
   - `UserStatusCheckNode` → Simplify
   - `PaymentRequestNode` → Convert to donation request

3. **Database Changes**:
   - Remove `tokens` column from users table
   - Remove token-related queries
   - Keep donation tracking

4. **Payment System**:
   - Remove token conversion logic
   - Simplify to direct donation processing
   - Keep Bitcoin payment infrastructure

## 🚀 **Migration Strategy**

### **Phase 1: Core System Changes**

#### **1.1 Update Flow Types**
```python
# src/pocketflow/core/types.py
class FlowType(str, Enum):
    """Types of flows based on user status."""
    DONATION_USER = "donation_user"  # Single flow type for all users
```

#### **1.2 Simplify User Status**
```python
# src/pocketflow/nodes/user_status.py
class UserStatusCheckNode(SimpleNode):
    """Node that checks user status (simplified for donation-only)."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Check user status and set flow type."""
        user_email = getattr(shared, 'user', None)
        
        if not user_email:
            return {"flow_type": FlowType.DONATION_USER.value}
        
        # All users get the same flow type
        return {
            "flow_type": FlowType.DONATION_USER.value,
            "user_email": user_email
        }
```

#### **1.3 Create Donation Request Node**
```python
# src/pocketflow/nodes/donation_request.py
class DonationRequestNode(SimpleNode):
    """Node that requests donations from users."""
    
    def process(self, shared: SharedState) -> Optional[Dict[str, Any]]:
        """Request donation and provide payment instructions."""
        user_email = getattr(shared, 'user', None)
        
        # Generate Bitcoin address for donation
        btc_address = self._get_or_create_btc_address(user_email)
        
        return {
            "donation_requested": True,
            "btc_address": btc_address,
            "message": "Thank you for using our service! Please consider making a donation to support continued development."
        }
```

### **Phase 2: Database Schema Updates**

#### **2.1 Remove Token Columns**
```sql
-- Migration script
ALTER TABLE users DROP COLUMN tokens;
ALTER TABLE users DROP COLUMN token_balance;
```

#### **2.2 Keep Donation Tracking**
```sql
-- Keep existing donation tables
-- payments table (for tracking donations)
-- btc_addresses table (for payment addresses)
```

### **Phase 3: Flow Simplification**

#### **3.1 Single Flow Type**
```yaml
# config/flows.yaml
flows:
  donation_user_flow:
    name: "Donation User Flow"
    description: "Unified flow for all users with donation support"
    flow_type: "donation_user"
    requires_tokens: false
    timeout: 300
    steps:
      - fetch_email
      - check_user_status
      - process_agent
      - generate_content
      - request_donation
      - send_email
```

#### **3.2 Simplified Flow Manager**
```python
# src/pocketflow/flows/manager.py
class FlowManager:
    def select_flow(self, shared: SharedState) -> str:
        """Select the appropriate flow (always donation flow)."""
        return "donation_user_flow"  # Single flow for all users
```

### **Phase 4: Payment System Updates**

#### **4.1 Simplify Payment Processing**
```python
# src/pocketflow/services/payment_monitor.py
class DonationMonitor:
    """Monitor for donations (no token conversion)."""
    
    def process_donation(self, tx: Dict) -> bool:
        """Process donation without token conversion."""
        # Log donation for tracking
        # Send thank you email
        # No token management needed
        return True
```

#### **4.2 Update Bitcoin Service**
```python
# src/pocketflow/services/bitcoin_service.py
class BitcoinService:
    def create_donation_request(self, user_email: str) -> Dict[str, Any]:
        """Create a donation request (no token conversion)."""
        btc_address = self.get_or_create_address(user_email)
        
        return {
            "btc_address": btc_address,
            "message": "Please consider making a donation to support our service.",
            "suggested_amount": "0.001 BTC"
        }
```

## 🔄 **Implementation Steps**

### **Step 1: Create New Flow Type**
1. Update `src/pocketflow/core/types.py`
2. Remove old flow types
3. Add `DONATION_USER` flow type

### **Step 2: Update User Status Logic**
1. Simplify `UserStatusCheckNode`
2. Remove token validation logic
3. Create `DonationRequestNode`

### **Step 3: Update Flow Configuration**
1. Replace `config/flows.yaml`
2. Remove token-based flows
3. Create single donation flow

### **Step 4: Update Database Schema**
1. Create migration script
2. Remove token columns
3. Keep donation tracking

### **Step 5: Update Payment System**
1. Simplify payment monitor
2. Remove token conversion
3. Keep Bitcoin infrastructure

### **Step 6: Update Email Templates**
1. Remove token-related messages
2. Add donation request templates
3. Update thank you messages

## 📊 **Benefits of Donation-Only Model**

### **For Users:**
- ✅ **Simplified Experience**: No token management
- ✅ **Transparent**: Direct donation support
- ✅ **Flexible**: Donate any amount
- ✅ **No Barriers**: Immediate access to all features

### **For System:**
- ✅ **Reduced Complexity**: Single flow type
- ✅ **Easier Maintenance**: Fewer components
- ✅ **Better UX**: No token confusion
- ✅ **Sustainable**: Voluntary donations

### **For Development:**
- ✅ **Faster Development**: Simpler codebase
- ✅ **Easier Testing**: Fewer edge cases
- ✅ **Better Debugging**: Less complex flows
- ✅ **Future-Proof**: Easier to extend

## 🎯 **Migration Timeline**

### **Week 1: Core Changes**
- [ ] Update flow types
- [ ] Simplify user status logic
- [ ] Create donation request node

### **Week 2: Database & Flows**
- [ ] Update database schema
- [ ] Create new flow configuration
- [ ] Update flow manager

### **Week 3: Payment & Email**
- [ ] Simplify payment system
- [ ] Update email templates
- [ ] Test donation flow

### **Week 4: Testing & Deployment**
- [ ] Comprehensive testing
- [ ] User communication
- [ ] Gradual rollout

## 🚨 **Risk Mitigation**

### **Data Migration**
- Keep existing donation data
- Archive token history
- Provide migration path for existing users

### **User Communication**
- Clear messaging about changes
- Explain donation benefits
- Provide support during transition

### **Rollback Plan**
- Keep token system code (commented)
- Database migration scripts
- Feature flags for gradual rollout

## 🎉 **Expected Outcomes**

1. **Simplified User Experience**: No token management
2. **Reduced System Complexity**: Single flow type
3. **Better User Engagement**: Voluntary donations
4. **Easier Maintenance**: Fewer components
5. **Sustainable Model**: Donation-based support

---

**Ready to simplify and improve the user experience! 🚀** 