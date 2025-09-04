from st_aggrid import AgGrid, GridOptionsBuilder
import streamlit as st

def render_aggrid(df, page_size=20, height=500):
    """Render AgGrid dengan setting default"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)
    gb.configure_default_column(editable=False, groupable=True, resizable=True, wrapText=True, autoHeight=True)

    # Atur minimal lebar tiap kolom
    for col in df.columns:
        gb.configure_column(col, minWidth=120)

    gridOptions = gb.build()
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        height=height,
        fit_columns_on_grid_load=True
    )
    return grid_response


def download_csv_button(df, filename="transaksi.csv"):
    """Tombol download CSV"""
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )
