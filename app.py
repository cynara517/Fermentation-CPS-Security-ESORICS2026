import streamlit as st
import pandas as pd
import json
import re
import time
from crewai import Agent, Task, Crew, LLM

# ==========================================
# 1. UI Aesthetics & Configuration
# ==========================================
st.set_page_config(page_title="ESORICS 2026 - Fermentation CPS Security", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&family=Inter:wght@300;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #e0e0e0; background-color: #0e1117; }
    h1, h2, h3 { color: #ffffff; border-bottom: 1px solid #333333; padding-bottom: 8px; }
    .pipeline-container { display: flex; justify-content: space-between; background-color: #1a1c23; padding: 15px 25px; border-radius: 8px; border-left: 5px solid #00ff88; margin-bottom: 25px; font-family: 'Fira Code', monospace; font-size: 0.9em; }
    .step-active { color: #00ff88; font-weight: bold; }
    .step-inactive { color: #555555; }
    .step-arrow { color: #888888; padding: 0 10px; }
    .data-stats-box { background-color: #1c2128; border: 1px solid #444c56; padding: 15px; border-radius: 6px; margin-bottom: 15px; font-family: 'Fira Code', monospace; }
    .data-highlight { color: #58a6ff; font-weight: bold; }
    .metrics-header { color: #00ff88; font-family: 'Fira Code', monospace; font-size: 1.1em; margin-top: 20px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Sidebar for API Credentials (安全机制：用户自带 Key)
# ==========================================
with st.sidebar:
    st.header("🔑 Security & Model Config")
    st.markdown("To prevent unauthorized access, please provide your LLM API credentials to execute the security agents.")
    user_api_key = st.text_input("MiniMax API Key", type="password", placeholder="Enter your API Key")
    user_group_id = st.text_input("MiniMax Group ID", type="password", placeholder="Enter your Group ID")
    st.markdown("---")
    st.markdown("*Note: Your credentials are used locally in this session and are never stored.*")

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match: return json.loads(match.group(0))
    raise ValueError("Valid JSON structure not found in the output.")

# ==========================================
# 3. Main UI Application
# ==========================================
st.title("🛡️ ICS Fermentation Anomaly Detection Framework")
st.markdown("Establishing Physics-Guided Baselines for Complex Batch Biochemical Processes (ESORICS 2026)")

st.markdown("""
<div class="pipeline-container">
    <span class="step-active">[▶ PHASE I: Physical Invariant Discovery]</span>
    <span class="step-arrow">➔</span>
    <span class="step-inactive">[ PHASE II: Normal Profile Parameter Identification ]</span>
</div>
""", unsafe_allow_html=True)

st.header("Phase I: Telemetry Data Input & Invariant Extraction")
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Fermentation Batch Sensor Logs (CSV)", type=["csv"])

with col2:
    user_prior = st.text_area("Prior Knowledge / Known Constraints (Optional)", placeholder="Example: Assume Haldane kinetics...")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    headers = df.columns.tolist()
    
    batch_cols = [col for col in headers if re.search(r'batch|run|id', col, re.IGNORECASE)]
    batch_info = f"<span class='data-highlight'>{df[batch_cols[0]].nunique()}</span> independent batches detected" if batch_cols else "Single continuous batch detected"

    st.markdown(f"""
    <div class="data-stats-box">
        <b>[System Telemetry Log Analysis]</b> Sensor data stream ready.<br>
        ▶ <b>Total Time Steps</b>: <span class="data-highlight">{len(df)}</span> | <b>Sensor Dimensions</b>: <span class="data-highlight">{len(df.columns)}</span><br>
        ▶ <b>Available Sensor Streams</b>: {headers}
    </div>
    """, unsafe_allow_html=True)

    if st.button("Initialize Multi-Agent Security Engine", type="primary"):
        
        # --- 安全拦截机制 ---
        if not user_api_key or not user_group_id:
            st.error("⚠️ Access Denied: Please provide your MiniMax API Key and Group ID in the left sidebar first.")
            st.stop()

        # 动态初始化 LLM
        minimax_llm = LLM(
            model="minimax/minimax-m2.7", 
            api_key=user_api_key,
            base_url="https://api.minimax.chat/v1",
            extra_headers={"Authorization": f"Bearer {user_api_key}", "x-group-id": user_group_id},
            temperature=0.1 
        )

        generator_agent = Agent(
            role='Lead Biochemical CPS Security Modeler',
            goal='Analyze sensor data from bio-fermentation systems to establish physical invariant models for anti-spoofing defense.',
            backstory="You are a CPS security expert. STRICTLY confine models to bio-fermentation processes (Biomass X, Substrate S, Product P, DO). DO NOT use unrelated models. Output in English.",
            llm=minimax_llm, verbose=True
        )

        reviewer_agent = Agent(
            role='Physical Consistency & Security Critic',
            goal='Strictly scrutinize fermentation kinetic models, eliminate unidentifiable parameters.',
            backstory="You are a strict reviewer. Reject models with coupled parameters (e.g., k1*k2) as attackers exploit their null-space. Ensure pure LaTeX. Output strictly JSON in English.",
            llm=minimax_llm, verbose=True
        )

        # ---------------------------------------------------------
        # 执行与计时
        # ---------------------------------------------------------
        t0_gen = time.time()
        with st.spinner("🤖 Agent 1 (Generator) is computing system null-space and extracting physical invariants..."):
            draft_task = Task(
                description=f"Propose a physical invariant model mapping based on:\n- Headers: {headers}\n- Prior: {user_prior}\nConfine domain to bio-fermentation!",
                expected_output="Preliminary mechanism draft.", agent=generator_agent
            )
            crew_gen = Crew(agents=[generator_agent], tasks=[draft_task])
            draft_output = crew_gen.kickoff()
        time_gen = time.time() - t0_gen
        
        t0_rev = time.time()
        with st.spinner("🕵️‍♂️ Agent 2 (Critic) is scrutinizing the proposed invariants for security vulnerabilities..."):
            review_task = Task(
                description=f"""
                Review the draft: {draft_output}
                Ensure parameters are identifiable. Output ONLY JSON:
                {{
                    "mechanism_name": "Model Name",
                    "theoretical_background": "Explanation for anti-spoofing defense.",
                    "review_status": {{"is_passed": true/false, "feedback": "Reason", "proposed_alternative": "Alternative"}},
                    "equations_color_coded": ["LaTeX with \\color{{blue}}{{Var}} and \\color{{red}}{{Param}}"],
                    "equations_original_vars": ["Engineering Reference mapping CSV headers"],
                    "mapping": [{{"data_header": "Header", "theory_var": "Symbol"}}],
                    "parameters_to_identify": [{{"symbol": "Symbol", "meaning": "Definition", "identified_by": ["CSV headers"]}}]
                }}
                """,
                expected_output="Strict JSON string.", agent=reviewer_agent
            )
            crew_rev = Crew(agents=[reviewer_agent], tasks=[review_task])
            raw_result = crew_rev.kickoff()
        time_rev = time.time() - t0_rev

        # ---------------------------------------------------------
        # 渲染结果
        # ---------------------------------------------------------
        try:
            res_data = extract_json(str(raw_result))
            st.markdown("---")
            st.header("II. Physical Invariant Security Report")
            
            st.markdown('<div class="metrics-header">⏱️ System Overhead & Execution Metrics</div>', unsafe_allow_html=True)
            st.table(pd.DataFrame({
                "Agent Role": ["Lead Biochemical Modeler", "Security Critic", "Pipeline Aggregate"],
                "Task Executed": ["Physical Invariant Extraction", "Identifiability & Null-Space Check", "Total Latency"],
                "Execution Time (s)": [f"{time_gen:.2f}", f"{time_rev:.2f}", f"{time_gen + time_rev:.2f}"]
            }))
            
            st.subheader(f"Establishing Baseline: {res_data['mechanism_name']}")
            st.info(f"**Physical Background for Defense**:\n{res_data['theoretical_background']}")
            
            status = res_data.get("review_status", {})
            if status.get("is_passed"): st.success("✔️ **STATUS: SECURE** – Parameters are independent. No covert null-space vulnerabilities detected.")
            else: st.error("❌ **STATUS: VULNERABLE**")
            
            st.subheader("Governing Differential Equations (Dual Reference)")
            col_eq1, col_eq2 = st.columns(2)
            with col_eq1:
                st.markdown("**1. Theoretical Version (Rendered)**")
                for eq in res_data.get("equations_color_coded", []): st.latex(eq) 
            with col_eq2:
                st.markdown("**2. Engineering Implementation Mapping**")
                for eq_orig in res_data.get("equations_original_vars", []): st.code(eq_orig, language="markdown")

            st.subheader("III. Parameter Target Space (Proceed to Phase II)")
            params_df = pd.DataFrame(res_data["parameters_to_identify"])
            params_df["identified_by"] = params_df["identified_by"].apply(lambda x: ", ".join(x))
            st.table(params_df)

        except Exception as e:
            st.error("Failed to parse the JSON output.")
            with st.expander("View Raw Agent Output"): st.write(str(raw_result))