# Electrum Deprecation Plan

## 🎯 **Overview**

This plan outlines the migration from Electrum wallet integration to a simpler Bitcoin address generation approach. The goal is to remove the complexity of wallet management while maintaining Bitcoin donation functionality.

## 📋 **Current Electrum Dependencies**

### **Files Using Electrum:**
1. `src/pocketflow/utils/electrum_utils.py` - Core Electrum utilities
2. `src/pocketflow/services/bitcoin_service.py` - Uses Electrum for address generation
3. `src/pocketflow/services/payment_monitor.py` - Uses Electrum for balance checking
4. `scripts/check_address_in_wallet.py` - Electrum wallet checking
5. `scripts/purge_invalid_addresses.py` - Electrum address validation
6. `check_payment.py` - Electrum balance checking
7. `src/pocketflow/config/models.py` - Electrum configuration

### **Electrum Functions to Replace:**
- `get_new_btc_address()` - Generate new addresses
- `get_wallet_addresses()` - List wallet addresses
- `check_address_in_wallet()` - Validate addresses
- `get_address_balance()` - Check address balances

## 🚀 **Simplified Bitcoin Address Strategy**

### **Option 1: External Bitcoin Service**
```python
# Use a public Bitcoin service API
def get_new_btc_address():
    """Generate address using external service."""
    response = requests.get("https://api.blockcypher.com/v1/btc/main/addrs")
    return response.json()["address"]
```

### **Option 2: Deterministic Address Generation**
```python
# Generate addresses deterministically from user email
def generate_address_from_email(email: str) -> str:
    """Generate deterministic address from email."""
    import hashlib
    import hdwallet
    
    # Create deterministic seed from email
    seed = hashlib.sha256(email.encode()).hexdigest()
    
    # Generate HD wallet and derive address
    wallet = hdwallet.HDWallet()
    wallet.from_seed(seed)
    wallet.from_path("m/44'/0'/0'/0/0")
    
    return wallet.address()
```

### **Option 3: Pre-generated Address Pool**
```python
# Use a pool of pre-generated addresses
def get_address_from_pool():
    """Get address from pre-generated pool."""
    # Load from database or file
    addresses = load_address_pool()
    return addresses.pop() if addresses else None
```

## 🔄 **Migration Strategy**

### **Phase 1: Create Simplified Bitcoin Service**

#### **1.1 Create New Bitcoin Utils**
```python
# src/pocketflow/utils/simple_bitcoin_utils.py
class SimpleBitcoinUtils:
    """Simplified Bitcoin utilities without Electrum."""
    
    def __init__(self):
        self.address_pool = []
        self.load_address_pool()
    
    def get_new_address(self, user_email: str) -> str:
        """Get a new Bitcoin address for user."""
        # Use deterministic generation or external service
        return self._generate_deterministic_address(user_email)
    
    def check_address_balance(self, address: str) -> float:
        """Check address balance using public API."""
        return self._get_balance_from_api(address)
```

#### **1.2 Update Bitcoin Service**
```python
# src/pocketflow/services/bitcoin_service.py
class BitcoinService:
    def _generate_address(self, user_email: str) -> str:
        """Generate address using simplified approach."""
        from ..utils.simple_bitcoin_utils import SimpleBitcoinUtils
        
        bitcoin_utils = SimpleBitcoinUtils()
        return bitcoin_utils.get_new_address(user_email)
```

### **Phase 2: Update Payment Monitor**

#### **2.1 Simplified Balance Checking**
```python
# src/pocketflow/services/donation_monitor.py
def get_address_balance(self, address: str) -> float:
    """Get balance using public API."""
    try:
        response = requests.get(f"https://blockchain.info/balance?active={address}")
        data = response.json()
        return data[address]["final_balance"] / 100000000  # Convert satoshis to BTC
    except Exception as e:
        self.logger.error(f"Failed to get balance for {address}: {e}")
        return 0.0
```

### **Phase 3: Remove Electrum Dependencies**

#### **3.1 Update Configuration**
```python
# src/pocketflow/config/models.py
class BitcoinConfig(BaseModel):
    """Simplified Bitcoin configuration."""
    use_external_api: bool = Field(default=True, description="Use external API for addresses")
    api_endpoint: str = Field(default="https://blockchain.info", description="Bitcoin API endpoint")
    address_pool_size: int = Field(default=100, description="Size of address pool")
```

#### **3.2 Remove Electrum Scripts**
- Delete `scripts/check_address_in_wallet.py`
- Delete `scripts/purge_invalid_addresses.py`
- Update `check_payment.py` to use simplified approach

## 🎯 **Recommended Approach**

### **Use External Bitcoin APIs:**
1. **BlockCypher API**: For address generation and balance checking
2. **Blockchain.info API**: For balance checking
3. **ElectrumX Public Servers**: For transaction monitoring

### **Benefits:**
- ✅ **No Wallet Management**: No need to maintain Electrum wallet
- ✅ **Simplified Setup**: No Electrum installation required
- ✅ **Better Reliability**: Public APIs are more reliable
- ✅ **Easier Maintenance**: No wallet synchronization issues
- ✅ **Scalable**: Can handle more users without wallet limits

## 🔄 **Implementation Steps**

### **Step 1: Create Simplified Bitcoin Utils**
1. Create `src/pocketflow/utils/simple_bitcoin_utils.py`
2. Implement address generation using external APIs
3. Implement balance checking using public APIs

### **Step 2: Update Services**
1. Update `src/pocketflow/services/bitcoin_service.py`
2. Update `src/pocketflow/services/donation_monitor.py`
3. Update `src/pocketflow/services/payment_monitor.py`

### **Step 3: Update Configuration**
1. Update `src/pocketflow/config/models.py`
2. Remove Electrum-specific settings
3. Add external API configuration

### **Step 4: Remove Electrum Dependencies**
1. Delete `src/pocketflow/utils/electrum_utils.py`
2. Delete Electrum-related scripts
3. Update imports throughout the codebase

### **Step 5: Test and Deploy**
1. Test address generation
2. Test balance checking
3. Test donation processing
4. Deploy to production

## 📊 **Benefits of Electrum Deprecation**

### **For System:**
- ✅ **Reduced Complexity**: No wallet management
- ✅ **Better Reliability**: Public APIs are more stable
- ✅ **Easier Setup**: No Electrum installation
- ✅ **Better Performance**: Faster API calls
- ✅ **Scalable**: No wallet limits

### **For Development:**
- ✅ **Simpler Codebase**: Fewer dependencies
- ✅ **Easier Testing**: No wallet setup required
- ✅ **Better Debugging**: Clear API responses
- ✅ **Future-Proof**: Standard APIs

### **For Users:**
- ✅ **Faster Setup**: No wallet configuration
- ✅ **Better Reliability**: No wallet sync issues
- ✅ **Transparent**: Clear API-based approach

## 🚨 **Migration Notes**

### **Data Migration:**
- Keep existing addresses in database
- Validate addresses using public APIs
- Remove invalid addresses

### **Backward Compatibility:**
- Keep Electrum code (commented) for rollback
- Gradual migration of address generation
- Test thoroughly before full deployment

### **Risk Mitigation:**
- Use multiple API providers
- Implement fallback mechanisms
- Monitor API rate limits
- Keep backup address generation methods

---

**Ready to simplify Bitcoin integration by removing Electrum! 🚀** 