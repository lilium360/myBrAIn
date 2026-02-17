import streamlit as st
import pandas as pd
import datetime
import hashlib
import json
from core.db import BrainDB
from core import config
from streamlit_agraph import agraph, Node, Edge, Config

# --- Page Setup ---
st.set_page_config(
     page_title="myBrAIn Central Command",
     page_icon="🧠",
     layout="wide",
     initial_sidebar_state="expanded"
)

# --- Premium Custom CSS ---
st.markdown("""
    <style>
    /* Main background and font */
    .main {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom Card Style */
    .memory-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .memory-card:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
        background-color: #1c2128;
    }
    .memory-type-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 8px;
        text-transform: uppercase;
    }
    .tag-rule { background-color: #238636; color: white; }
    .tag-context { background-color: #1f6feb; color: white; }
    .tag-constraint { background-color: #da3633; color: white; }
    
    .card-content {
        color: #c9d1d9;
        font-size: 0.95rem;
        margin-top: 10px;
        line-height: 1.5;
    }
    .card-footer {
        margin-top: 15px;
        font-size: 0.8rem;
        color: #8b949e;
        display: flex;
        justify-content: space-between;
    }
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #58a6ff;
    }
    
    /* Button overrides */
    .stButton>button {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Persistence ---
@st.cache_resource
def get_db():
    return BrainDB()

db = get_db()

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
        
        # Enrich rows missing project_name
        if not full_df.empty:
            name_map = full_df[full_df["project_name"] != "Unknown"].set_index("workbase_id")["project_name"].to_dict()
            full_df["project_name"] = full_df.apply(
                lambda row: name_map.get(row["workbase_id"], row["project_name"]), axis=1
            )
            
        return full_df
    except Exception as e:
        st.error(f"Error loading system memory: {e}")
        return pd.DataFrame()

# --- CRUD Operations ---
def delete_memories(ids):
    try:
        db.collection.delete(ids=ids)
        st.success(f"Successfully deleted {len(ids)} memories.")
        st.cache_resource.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Deletion failed: {e}")

def update_memory_metadata(memory_id, text, metadata):
    try:
        db.collection.update(
            ids=[memory_id],
            documents=[text],
            metadatas=[metadata]
        )
        return True
    except Exception as e:
        st.error(f"Update failed for {memory_id}: {e}")
        return False

# --- UI Components ---
def render_memory_card(row):
    tag_class = f"tag-{row['type']}"
    st.markdown(f"""
        <div class="memory-card">
            <div>
                <span class="memory-type-tag {tag_class}">{row['type']}</span>
                <span style="color: #8b949e; font-size: 0.8rem;">{row['category']}</span>
            </div>
            <div class="card-content">{row['text']}</div>
            <div class="card-footer">
                <span>📂 {row['project_name']}</span>
                <span>🕒 {row['created_at'][:10] if row['created_at'] != 'N/A' else 'N/A'}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- Main Logic ---
df = load_data()

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/parakeet/96/brain.png", width=60)
    st.title("myBrAIn Admin")
    
    if st.button("🔄 Refresh Data", use_container_width=True, type="secondary"):
        st.cache_resource.clear()
        st.rerun()

    st.divider()
    
    st.header("🔍 Filters")
    workbase_filter = "All"
    category_filter = []
    
    if not df.empty:
        wb_names = df.groupby("workbase_id")["project_name"].first().to_dict()
        wb_options = {f"{name} ({wb_id[:6]})": wb_id for wb_id, name in wb_names.items()}
        
        selected_display = st.selectbox("Workbase", ["All"] + sorted(list(wb_options.keys())))
        workbase_filter = wb_options.get(selected_display, "All")
        
        categories = sorted(df["category"].unique().tolist())
        category_filter = st.multiselect("Category", categories)

    st.divider()
    
    with st.expander("⚙️ System Settings", expanded=False):
        st.caption(f"**DB:** {config.BASE_DATA_DIR.name}")
        st.caption(f"**Model:** {config.EMBEDDING_MODEL.split('/')[-1]}")
        
        st.write("---")
        st.warning("Danger Zone")
        if st.checkbox("Enable Workbase Destruction"):
            target_wb = st.selectbox("Select Workbase to Destroy", ["None"] + sorted(list(wb_options.keys())))
            if target_wb != "None":
                wb_id_to_del = wb_options[target_wb]
                if st.button(f"🔥 DESTROY {target_wb}", type="primary", use_container_width=True):
                    # Confirmation via Text Input
                    st.session_state.confirm_delete = True
                
                if st.session_state.get('confirm_delete'):
                    confirm_text = st.text_input(f"Type 'DELETE {target_wb.split(' ')[0]}' to confirm:")
                    if confirm_text == f"DELETE {target_wb.split(' ')[0]}":
                        # Perform deletion of all items with this workbase_id
                        ids_to_del = df[df["workbase_id"] == wb_id_to_del]["id"].tolist()
                        if ids_to_del:
                            db.collection.delete(ids=ids_to_del)
                            st.success(f"Workbase {target_wb} destroyed.")
                            st.session_state.confirm_delete = False
                            st.cache_resource.clear()
                            st.rerun()

# --- Main Content ---
st.title("🧠 Command Center")
st.caption("Advanced Semantic Memory Management")

if not df.empty:
    # Filter data
    display_df = df.copy()
    if workbase_filter != "All":
        display_df = display_df[display_df["workbase_id"] == workbase_filter]
    if category_filter:
        display_df = display_df[display_df["category"].isin(category_filter)]

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", len(display_df))
    m2.metric("Rules", len(display_df[display_df["type"]=="rule"]))
    m3.metric("Constraints", len(display_df[display_df["category"]=="constraints"]))
    m4.metric("Categories", len(display_df["category"].unique()))

    st.divider()

    tab_explore, tab_graph, tab_raw, tab_inject = st.tabs([
        "🗂️ Card View", 
        "🕸️ Knowledge Graph",
        "📑 Grid Editor",
        "💉 Injection"
    ])

    with tab_explore:
        if not display_df.empty:
            # Multi-select using st.data_editor hidden but driving selection? 
            # Or just cards. Cards are better for UX as requested.
            cols = st.columns(3)
            for i, (_, row) in enumerate(display_df.iterrows()):
                with cols[i % 3]:
                    render_memory_card(row)
        else:
            st.info("No memories match the filters.")

    with tab_graph:
        st.subheader("Semantic Relationships")
        if not display_df.empty:
            nodes = []
            edges = []
            # For visualization, we limit nodes if too many
            limit = 50
            viz_df = display_df.head(limit)
            
            for _, row in viz_df.iterrows():
                color = "#238636" if row['type'] == 'rule' else "#1f6feb"
                if row['type'] == 'constraint': color = "#da3633"
                
                nodes.append(Node(
                    id=row['id'], 
                    label=row['category'], 
                    title=row['text'],
                    size=15,
                    color=color
                ))
            
            # Simple edges: connect same category within the same workbase
            for cat in viz_df['category'].unique():
                cat_nodes = viz_df[viz_df['category'] == cat]['id'].tolist()
                for i in range(len(cat_nodes)-1):
                    edges.append(Edge(source=cat_nodes[i], target=cat_nodes[i+1], type="CURVE_SMOOTH"))

            config_graph = Config(width=1000, height=600, directed=True, nodeHighlightBehavior=True)
            agraph(nodes=nodes, edges=edges, config=config_graph)
        else:
            st.warning("Not enough data for graph visualization.")

    with tab_raw:
        st.subheader("Bulk Operations")
        # Global Actions
        col_act1, col_act2, col_spacer = st.columns([1, 1, 4])
        
        # We use st.data_editor with a checkbox column for selection
        display_df_with_sel = display_df.copy()
        display_df_with_sel.insert(0, "select", False)
        
        edited_raw = st.data_editor(
            display_df_with_sel,
            column_config={
                "select": st.column_config.CheckboxColumn("Select", default=False),
                "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
                "text": st.column_config.TextColumn("Content", width="large"),
                "project_name": st.column_config.TextColumn("Project", disabled=True),
                "workbase_id": None,
                "category": st.column_config.SelectboxColumn("Category", options=sorted(df["category"].unique().tolist())),
                "type": st.column_config.SelectboxColumn("Type", options=["rule", "context", "constraint"]),
            },
            hide_index=True,
            use_container_width=True,
            key="bulk_editor"
        )
        
        selected_ids = edited_raw[edited_raw["select"] == True]["id"].tolist()
        
        if col_act1.button("🗑️ Delete Selected", type="primary", disabled=not selected_ids):
            delete_memories(selected_ids)
            
        if col_act2.button("💾 Save Grid", disabled=True): # Save logic similar to original but filtered
            pass
        st.caption(f"Selected: {len(selected_ids)} items")

    with tab_inject:
        st.subheader("Manual Knowledge Injection")
        with st.form("injection_form", clear_on_submit=True):
            selected_wb_display = st.selectbox("Target Workbase", sorted(list(wb_options.keys())))
            target_workbase = wb_options[selected_wb_display]
            i_type = st.selectbox("Type", ["rule", "context", "constraint"])
            i_category = st.text_input("Category", placeholder="e.g., coding_style")
            i_content = st.text_area("Memory Content", height=150)
            
            if st.form_submit_button("🚀 Inject Memory", type="primary"):
                if i_content and i_category:
                    content_hash = hashlib.md5(i_content.encode("utf-8")).hexdigest()
                    new_id = f"{i_type}_{target_workbase}_{content_hash}"
                    metadata = {
                        "workbase_id": target_workbase,
                        "type": i_type,
                        "category": i_category,
                        "source": "manual",
                        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                        "schema_version": config.DB_SCHEMA_VERSION,
                        "project_name": selected_wb_display.split(" (")[0]
                    }
                    db.add_memory(new_id, i_content, metadata)
                    st.success(f"Injected ID: {new_id}")
                    st.cache_resource.clear()
                    st.rerun()

else:
    st.warning("No memories found. Initialize a workbase first.")
    if st.sidebar.button("Retry"): st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("myBrAIn Core v1.1 — © 2026")
