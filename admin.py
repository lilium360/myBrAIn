import streamlit as st
import pandas as pd
from core.db import BrainDB
from core import config

st.set_page_config(page_title="myBrAIn Admin", layout="wide")

st.title("🧠 myBrAIn — Admin UI")
st.markdown("---")

db = BrainDB()

# Sidebar - Filter by Workbase ID
st.sidebar.header("Filters")
all_memories = []

# Fetch all data from ChromaDB (simplified for admin)
# In production, we would use a more efficient way to list collections
try:
    results = db.collection.get()
    
    if results["ids"]:
        for i in range(len(results["ids"])):
            all_memories.append({
                "id": results["ids"][i],
                "text": results["documents"][i],
                "workbase_id": results["metadatas"][i].get("workbase_id"),
                "type": results["metadatas"][i].get("type"),
                "category": results["metadatas"][i].get("category"),
                "created_at": results["metadatas"][i].get("created_at")
            })
    
    df = pd.DataFrame(all_memories)
except Exception as e:
    st.error(f"Error loading memories: {e}")
    df = pd.DataFrame()

if not df.empty:
    workbases = df["workbase_id"].unique().tolist()
    selected_workbase = st.sidebar.selectbox("Filter by Workbase", ["All"] + workbases)
    
    if selected_workbase != "All":
        df = df[df["workbase_id"] == selected_workbase]

    st.subheader(f"Stored Memories ({len(df)})")
    
    # Editable Table
    edited_df = st.data_editor(
        df,
        column_config={
            "id": st.column_config.TextColumn("ID", disabled=True),
            "text": st.column_config.TextColumn("Memory Content", width="large"),
            "workbase_id": st.column_config.TextColumn("Workbase", disabled=True),
            "type": st.column_config.TextColumn("Type", disabled=True),
            "category": st.column_config.TextColumn("Category"),
            "created_at": st.column_config.TextColumn("Date", disabled=True),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("Save Changes"):
        # Logic to update modified rows
        # For simplicity in Core v1, we compare and update
        for index, row in edited_df.iterrows():
            orig_row = df[df["id"] == row["id"]]
            if not orig_row.empty:
                if row["text"] != orig_row.iloc[0]["text"]:
                    db.update_memory(row["id"], row["text"])
                    st.success(f"Updated memory {row['id']}")
        
        # New rows logic could be added here
        st.info("Re-syncing with database...")
        st.rerun()

else:
    st.info("No memories found. Initialize a workbase via the MCP server first.")

st.sidebar.markdown("---")
st.sidebar.info(f"DB Path: {config.BASE_DATA_DIR}")
st.sidebar.info(f"Schema Version: {config.DB_SCHEMA_VERSION}")
