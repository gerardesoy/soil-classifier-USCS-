import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# PART 1: THE LOGIC ENGINE
# ==========================================

def calculate_components(p200, p4):
    pct_fines = p200
    pct_gravel = 100 - p4
    pct_sand = p4 - p200
    if pct_sand < 0: pct_sand = 0
    if pct_gravel < 0: pct_gravel = 0
    return pct_gravel, pct_sand, pct_fines

def get_fine_grained_symbol(ll, pi, is_organic):
    a_line = 0.73 * (ll - 20)
    if is_organic:
        return "OH" if ll >= 50 else "OL"
    else:
        if ll >= 50:
            return "CH" if pi >= a_line else "MH"
        else:
            if pi > 7 and pi >= a_line: return "CL"
            elif pi < 4 or pi < a_line: return "ML"
            else: return "CL-ML"

def classify_coarse_grained(pct_gravel, pct_sand, pct_fines, ll, pi, cu, cc):
    if pct_gravel > pct_sand:
        prefix = "G"
        cu_crit = 4 
    else:
        prefix = "S"
        cu_crit = 6 
        
    a_line = 0.73 * (ll - 20)
    
    def get_fines_let(p_idx):
        if p_idx < 4 or p_idx < a_line: return "M"
        elif p_idx > 7 and p_idx >= a_line: return "C"
        else: return "M-C"

    grad_let = "P"
    if cu is not None and cc is not None:
        is_well = (cu >= cu_crit) and (1 <= cc <= 3)
        grad_let = "W" if is_well else "P"

    if pct_fines < 5:
        return f"{prefix}{grad_let}"
    elif pct_fines > 12:
        fines_let = get_fines_let(pi)
        if fines_let == "M-C": return f"{prefix}C-{prefix}M" 
        return f"{prefix}{fines_let}"
    else:
        fines_let = get_fines_let(pi)
        if fines_let == "M-C": fines_let = "M"
        return f"{prefix}{grad_let}-{prefix}{fines_let}"

def get_name_fine(symbol, pct_gravel, pct_sand, plus_200):
    base_map = {
        "CL": "Lean clay", "ML": "Silt", "OL": "Organic silt",
        "CH": "Fat clay", "MH": "Elastic silt", "OH": "Organic clay",
        "CL-ML": "Silty clay"
    }
    base = base_map.get(symbol, "Soil")
    if plus_200 < 15: return base
    elif 15 <= plus_200 < 30:
        if pct_sand >= pct_gravel: return f"{base} with sand"
        else: return f"{base} with gravel"
    else:
        if pct_sand >= pct_gravel:
            return f"Sandy {base.lower()}" if pct_gravel < 15 else f"Sandy {base.lower()} with gravel"
        else:
            return f"Gravelly {base.lower()}" if pct_sand < 15 else f"Gravelly {base.lower()} with sand"

def get_name_coarse(symbol, pct_gravel, pct_sand):
    has_gravel = pct_gravel >= 15
    has_sand = pct_sand >= 15

    # SPECIALS
    if symbol == "SC-SM": return "Silty clayey sand with gravel" if has_gravel else "Silty clayey sand"
    if symbol == "SM-SC": return "Silty clayey sand with gravel" if has_gravel else "Silty clayey sand"
    if symbol == "GC-GM": return "Silty clayey gravel with sand" if has_sand else "Silty clayey gravel"
    if symbol == "GM-GC": return "Silty clayey gravel with sand" if has_sand else "Silty clayey gravel"

    # DUALS
    if symbol == "SW-SM": return "Well-graded sand with silt and gravel" if has_gravel else "Well-graded sand with silt"
    if symbol == "SW-SC": return "Well-graded sand with clay and gravel" if has_gravel else "Well-graded sand with clay"
    if symbol == "SP-SM": return "Poorly graded sand with silt and gravel" if has_gravel else "Poorly graded sand with silt"
    if symbol == "SP-SC": return "Poorly graded sand with clay and gravel" if has_gravel else "Poorly graded sand with clay"
    if symbol == "GW-GM": return "Well-graded gravel with silt and sand" if has_sand else "Well-graded gravel with silt"
    if symbol == "GW-GC": return "Well-graded gravel with clay and sand" if has_sand else "Well-graded gravel with clay"
    if symbol == "GP-GM": return "Poorly graded gravel with silt and sand" if has_sand else "Poorly graded gravel with silt"
    if symbol == "GP-GC": return "Poorly graded gravel with clay and sand" if has_sand else "Poorly graded gravel with clay"

    # SINGLES
    if symbol == "GW": return "Well-graded gravel with sand" if has_sand else "Well-graded gravel"
    if symbol == "GP": return "Poorly graded gravel with sand" if has_sand else "Poorly graded gravel"
    if symbol == "GM": return "Silty gravel with sand" if has_sand else "Silty gravel"
    if symbol == "GC": return "Clayey gravel with sand" if has_sand else "Clayey gravel"
    if symbol == "SW": return "Well-graded sand with gravel" if has_gravel else "Well-graded sand"
    if symbol == "SP": return "Poorly graded sand with gravel" if has_gravel else "Poorly graded sand"
    if symbol == "SM": return "Silty sand with gravel" if has_gravel else "Silty sand"
    if symbol == "SC": return "Clayey sand with gravel" if has_gravel else "Clayey sand"

    return "Unknown Soil Name"

# ==========================================
# PART 2: THE STREAMLIT UI
# ==========================================

st.set_page_config(page_title="USCS Soil Classifier", page_icon="🌱")

st.title("ASTM D2487 Soil Classifier")
st.markdown("Enter your sieve and plasticity data below to classify the soil.")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Sieve Analysis")
p200 = st.sidebar.number_input("Percent Passing No. 200 (%)", min_value=0.0, max_value=100.0, value=18.0)
p4 = st.sidebar.number_input("Percent Passing No. 4 (%)", min_value=0.0, max_value=100.0, value=100.0)

st.sidebar.header("2. Atterberg Limits")
ll = st.sidebar.number_input("Liquid Limit (LL)", min_value=0.0, value=0.0)
pi_input_method = st.sidebar.radio("Input Method:", ["PI directly", "Calculate from PL"])

if pi_input_method == "PI directly":
    pi_val = st.sidebar.text_input("Plasticity Index (PI) or 'NP'", value="5")
    try:
        if pi_val.upper() == "NP":
            pi = 0.0
        else:
            pi = float(pi_val)
    except:
        pi = 0.0
else:
    pl_val = st.sidebar.number_input("Plastic Limit (PL)", value=0.0)
    pi = ll - pl_val
    st.sidebar.info(f"Calculated PI: {pi}")

# --- ORGANIC CHECK ---
with st.sidebar.expander("Organic Soil Check (Optional)"):
    ll_oven = st.number_input("LL Oven Dried", value=0.0)
    is_organic = False
    if ll_oven > 0 and ll > 0:
        if (ll_oven / ll) < 0.75:
            is_organic = True
            st.error("Soil is ORGANIC")

# --- GRADING CHECK ---
cu, cc = None, None
if p200 <= 12 and p200 < 50:
    with st.sidebar.expander("Grading Coefficients (Required for Coarse)", expanded=True):
        input_type = st.radio("Grading Input:", ["Enter Cu/Cc", "Enter D-sizes"])
        
        if input_type == "Enter Cu/Cc":
            cu = st.number_input("Coefficient of Uniformity (Cu)", value=0.0)
            cc = st.number_input("Coefficient of Curvature (Cc)", value=0.0)
        else:
            st.write("Enter grain sizes in mm:")
            d10 = st.number_input("D10", value=0.0, format="%.3f")
            d30 = st.number_input("D30", value=0.0, format="%.3f")
            d60 = st.number_input("D60", value=0.0, format="%.3f")
            
            # THE FIX: Only calculate if D10 and D60 are not zero
            if d10 > 0 and d60 > 0:
                cu = d60 / d10
                cc = (d30**2) / (d10 * d60)
                st.info(f"Calculated: Cu={cu:.2f}, Cc={cc:.2f}")
            else:
                st.warning("Please enter valid D10 and D60 values (must be > 0).")

# ==========================================
# PART 3: MAIN DISPLAY & PLOTS
# ==========================================

# 1. RUN CLASSIFICATION LOGIC
pct_gravel, pct_sand, pct_fines = calculate_components(p200, p4)
plus_200 = 100 - p200

if p200 >= 50:
    symbol = get_fine_grained_symbol(ll, pi, is_organic)
    name = get_name_fine(symbol, pct_gravel, pct_sand, plus_200)
else:
    symbol = classify_coarse_grained(pct_gravel, pct_sand, pct_fines, ll, pi, cu, cc)
    name = get_name_coarse(symbol, pct_gravel, pct_sand)

# 2. SHOW TEXT RESULTS
st.subheader("Classification Result")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Group Symbol", value=symbol)
with col2:
    st.info(f"**Group Name:**\n\n{name}")

st.write(f"**Components:** 🪨 Gravel: {pct_gravel:.1f}% | ⏳ Sand: {pct_sand:.1f}% | 🌫️ Fines: {pct_fines:.1f}%")

# --- U-LINE CHECK ---
# Calculate the max PI allowed for this specific LL

pi_max = 0.9 * (ll - 8)

if pi > pi_max and pi > 0:
    st.error(f"⚠️ Warning: Your point ({ll}, {pi}) plots above the U-Line!")
    st.warning("This indicates a likely error in your test data. Natural soils generally do not plot in this region. Please verify your Liquid Limit and Plastic Limit values.")

# 3. PLOT PLASTICITY CHART
st.subheader("Plasticity Chart Visualization")

# Create the figure
fig, ax = plt.subplots(figsize=(8, 6))

# --- DYNAMIC SCALING ---
max_x = max(100, ll + 20)
max_y = max(70, pi + 20)

# A. SETUP LINES
x = np.linspace(0, max_x, 200)

# A-Line: PI = 0.73(LL - 20)
a_line = 0.73 * (x - 20)
a_line[a_line < 0] = 0

# U-Line: PI = 0.9(LL - 8)
u_line = 0.9 * (x - 8)
u_line[u_line < 0] = 0

# Plot Lines
ax.plot(x, a_line, 'b-', linewidth=2, label="A-Line")
ax.plot(x, u_line, 'k--', linewidth=1.5, label="U-Line")
ax.axvline(x=50, color='k', linestyle='-', linewidth=1)

# B. HATCHED ZONE (CL-ML)
ax.fill_between(x, np.maximum(a_line, 4), 7, 
                where=(x > 10) & (x < 29.6) & (7 > a_line),
                facecolor='none', hatch='///', edgecolor='gray', alpha=0.5, label="CL-ML Zone")

# C. LABELS (Positioned & Opacity)
def get_mid_y(x_val):
    a_y = 0.73 * (x_val - 20)
    u_y = 0.9 * (x_val - 8)
    return (a_y + u_y) / 2

# High Plasticity
ax.text(77, get_mid_y(75), "CH or OH", fontsize=12, color='blue', ha='center', alpha=0.4, weight='bold')
ax.text(75, 20, "MH or OH", fontsize=12, color='blue', ha='center', alpha=0.4, weight='bold')

# Low Plasticity
ax.text(37, get_mid_y(35), "CL or OL", fontsize=12, color='blue', ha='center', alpha=0.4, weight='bold')
ax.text(40, 6, "ML or OL", fontsize=12, color='blue', ha='center', alpha=0.4, weight='bold')
ax.text(25, 8, "CL-ML",    fontsize=10, color='gray', ha='center', alpha=0.6)

# D. PLOT USER DATA
ax.plot(ll, pi, 'ro', markersize=12, markeredgecolor='white', markeredgewidth=2, label="Your Soil", zorder=5)
ax.text(ll + 2, pi, f"({ll}, {pi})", fontsize=10, color='black', fontweight='bold')

# E. FORMATTING
ax.set_xlim(0, max_x)
ax.set_ylim(0, max_y)
ax.set_xlabel("Liquid Limit (LL)")
ax.set_ylabel("Plasticity Index (PI)")
ax.set_title("ASTM D2487 Plasticity Chart")
ax.legend(loc='upper left')
ax.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)
