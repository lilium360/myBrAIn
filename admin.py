import streamlit as st
import pandas as pd
import datetime
import hashlib
from core.db import BrainDB
from core import config

# --- Page Setup ---
st.set_page_config(
    page_title="myBrAIn Central Command",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme/Style Customization (Optional/Subtle) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading Logic ---
@st.cache_resource
def get_db_connection():
    return BrainDB()

db = get_db_connection()

def load_data():
    all_memories = []
    try:
        results = db.collection.get()
        if results["ids"]:
            for i in range(len(results["ids"])):
                all_memories.append({
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "workbase_id": results["metadatas"][i].get("workbase_id"),
                    "project_name": results["metadatas"][i].get("project_name", "Unknown"),
                    "type": results["metadatas"][i].get("type", "unknown"),
                    "category": results["metadatas"][i].get("category", "unknown"),
                    "created_at": results["metadatas"][i].get("created_at", "N/A"),
                    "source": results["metadatas"][i].get("source", "agent")
                })
        
        full_df = pd.DataFrame(all_memories)
        
        # Enrich rows missing project_name by mapping workbase_id -> project_name
        # using 'context' entries as the source of truth
        if not full_df.empty:
            name_map = full_df[full_df["project_name"] != "Unknown"].set_index("workbase_id")["project_name"].to_dict()
            full_df["project_name"] = full_df.apply(
                lambda row: name_map.get(row["workbase_id"], row["project_name"]), axis=1
            )
            
        return full_df
    except Exception as e:
        st.error(f"Error loading system memory: {e}")
        return pd.DataFrame()

# --- Application Logic ---
df = load_data()

# --- Sidebar ---
wb_options = {}
with st.sidebar:
    st.image("https://img.icons8.com/parakeet/96/brain.png", width=80)
    st.title("Admin Navigation")
    
    if st.button("🔄 Force Refresh", use_container_width=True, type="secondary"):
        st.cache_resource.clear()
        st.rerun()

    st.divider()
    
    st.header("🔍 Global Filters")
    
    workbase_filter = "All"
    category_filter = []
    
    if not df.empty:
        # Create a display name mapping for workbases: ID -> "Project Name (ID_short)"
        wb_names = df.groupby("workbase_id")["project_name"].first().to_dict()
        wb_options = {f"{name} ({wb_id[:8]})": wb_id for wb_id, name in wb_names.items()}
        
        selected_display = st.selectbox("Filter by Workbase", ["All"] + sorted(list(wb_options.keys())))
        workbase_filter = wb_options.get(selected_display, "All")
        
        categories = sorted(df["category"].unique().tolist())
        category_filter = st.multiselect("Filter by Category", categories)

    st.divider()
    
    with st.expander("ℹ️ System Info"):
        st.caption(f"**DB Path:** {config.BASE_DATA_DIR}")
        st.caption(f"**Schema Version:** {config.DB_SCHEMA_VERSION}")
        st.caption(f"**Model:** {config.EMBEDDING_MODEL}")
        st.caption(f"**Conflict Threshold:** {config.CONFLICT_DISTANCE_THRESHOLD}")

# --- Main Dashboard ---
st.title("🧠 myBrAIn — Command Center")
st.caption("Deterministic Second Brain Management Interface")

if not df.empty:
    # Filter working data
    display_df = df.copy()
    if workbase_filter != "All":
        display_df = display_df[display_df["workbase_id"] == workbase_filter]
    if category_filter:
        display_df = display_df[display_df["category"].isin(category_filter)]

    # Metrics Section (omitted unchanged part for brevity, but I must include it in replacement)
    m1, m2, m3, m4 = st.columns(4)
    
    total_memories = len(display_df)
    active_rules = len(display_df[display_df["type"] == "rule"])
    constraints = len(display_df[display_df["category"] == "constraints"])
    
    last_act = "N/A"
    if not display_df.empty:
        try:
            last_date_str = display_df["created_at"].max()
            if last_date_str != "N/A":
                dt = datetime.datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))
                last_act = dt.strftime("%Y-%m-%d %H:%M")
        except:
            pass

    m1.metric("Total Memories", total_memories)
    m2.metric("Active Rules", active_rules)
    m3.metric("Constraints", constraints)
    m4.metric("Last Activity", last_act)

    st.divider()

    # Tabs Section
    tab_explorer, tab_injection, tab_analytics = st.tabs([
        "🗂️ Memory Explorer", 
        "💉 Brain Injection", 
        "📊 Analytics Lite"
    ])

    with tab_explorer:
        st.subheader("Persistent Knowledge Graph")
        
        edited_df = st.data_editor(
            display_df,
            column_config={
                "id": st.column_config.TextColumn("ID", disabled=True, width="small", help="Deterministic Hash ID"),
                "project_name": st.column_config.TextColumn("Project", disabled=True, width="medium"),
                "text": st.column_config.TextColumn("Memory Content", width="large", help="The semantic text stored in memory"),
                "workbase_id": None, # Hide the raw hash ID column if we have project name
                "category": st.column_config.SelectboxColumn(
                    "Category", 
                    options=sorted(df["category"].unique().tolist()),
                    required=True
                ),
                "type": st.column_config.SelectboxColumn(
                    "Type",
                    options=["rule", "context", "constraint"],
                    required=True
                ),
                "source": st.column_config.TextColumn("Source", disabled=True, width="small"),
                "created_at": st.column_config.TextColumn("Timestamp", disabled=True, width="medium"),
            },
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="editor"
        )

        col_save, col_empty = st.columns([1, 4])
        if col_save.button("💾 Save All Changes", type="primary", use_container_width=True):
            # Detection of changes
            changed_rows = 0
            for index, row in edited_df.iterrows():
                # Check for deletions in data_editor is complex with 'dynamic', handled via comparison
                # Here we handle updates to existing rows
                orig_row_matches = df[df["id"] == row["id"]]
                if not orig_row_matches.empty:
                    orig_row = orig_row_matches.iloc[0]
                    if row["text"] != orig_row["text"] or row["category"] != orig_row["category"] or row["type"] != orig_row["type"]:
                        # For simplicity, we update text. Metadata update requires collection.update with metadatas
                        db.collection.update(
                            ids=[row["id"]],
                            documents=[row["text"]],
                            metadatas=[{
                                "workbase_id": row["workbase_id"],
                                "type": row["type"],
                                "category": row["category"],
                                "source": row["source"],
                                "created_at": row["created_at"],
                                "schema_version": config.DB_SCHEMA_VERSION
                            }]
                        )
                        changed_rows += 1
            
            if changed_rows > 0:
                st.success(f"Successfully synchronized {changed_rows} updates to persistent storage.")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.info("No modifications detected.")

    with tab_injection:
        st.subheader("Manual Knowledge Injection")
        st.info("Directly inject rules or context into the brain. Conflict detection will NOT be bypassable if implemented in the server, but here we use the DB layer directly.")
        
        with st.form("injection_form", clear_on_submit=True):
            selected_wb_display = st.selectbox("Target Workbase", sorted(list(wb_options.keys())))
            target_workbase = wb_options[selected_wb_display]
            i_type = st.selectbox("Type", ["rule", "context", "constraint"])
            i_category = st.text_input("Category", placeholder="e.g., coding_style, naming_convention")
            i_content = st.text_area("Memory Content", placeholder="Enter the rule or context in English...", height=150)
            
            submit = st.form_submit_button("🚀 Inject Memory", type="primary")
            
            if submit:
                if not i_content or not i_category:
                    st.error("Content and Category are mandatory.")
                else:
                    # Deterministic ID for rules
                    content_hash = hashlib.md5(i_content.encode("utf-8")).hexdigest()
                    new_id = f"{i_type}_{target_workbase}_{content_hash}"
                    
                    metadata = {
                        "workbase_id": target_workbase,
                        "type": i_type,
                        "category": i_category,
                        "source": "manual",
                        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "schema_version": config.DB_SCHEMA_VERSION
                    }
                    
                    try:
                        db.add_memory(new_id, i_content, metadata)
                        st.success(f"Memory successfully injected! ID: {new_id}")
                        st.cache_resource.clear()
                    except Exception as e:
                        st.error(f"Injection failed: {e}")

    with tab_analytics:
        st.subheader("Brain Analytics")
        if not display_df.empty:
            cat_counts = display_df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            
            st.bar_chart(cat_counts, x="Category", y="Count", color="Category")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Memory Type Distribution**")
                type_counts = display_df["type"].value_counts()
                st.write(type_counts)
            with col_b:
                st.write("**Workbase Utilization**")
                wb_counts = df["workbase_id"].value_counts()
                st.write(wb_counts)
        else:
            st.warning("No data available for analytics.")

else:
    st.warning("No memories found. Link a project using `initialize_workbase` tool first.")
    if st.sidebar.button("Retry Loading"):
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("myBrAIn Core v1.0 — © 2026")
