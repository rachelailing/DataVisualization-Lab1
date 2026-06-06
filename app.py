import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Superstore Sales Analysis", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Sample - Superstore.csv', encoding='latin1')
    df['Unit Price'] = df['Sales'] / df['Quantity']
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

try:
    df = load_data()

    # --- SIDEBAR NAVIGATION ---
    st.sidebar.title("Navigation")
    view_selection = st.sidebar.radio(
        "Select a View",
        [
            "Basic Analysis", 
            "Bar Chart + Scatter Plot", 
            "Line Chart + Histogram", 
            "Pie Chart + Bar Chart", 
            "Geographic View + Scatter Plot"
        ]
    )

    # Consistent color palette for categories
    category_colors = ["#ff9999", "#66b3ff", "#99ff99"] 
    category_scale = alt.Scale(domain=['Furniture', 'Office Supplies', 'Technology'], range=category_colors)

    if view_selection == "Basic Analysis":
        st.title('Basic Sales Analysis')
        
        st.markdown("""
        ### How to Navigate this View
        * **Filter Data:** Use the **sidebar sliders** to set a sales range and the **dropdown** to select a specific category.
        * **Interactive Charts:** Hover over the bars or pie slices to see detailed values and percentages.
        * **Automatic Updates:** All charts update instantly as you adjust the filters.
        """)

        st.sidebar.header("Filters")
        
        # Enhanced Slider
        min_sales = 0.0
        max_sales = float(df['Sales'].max())
        sales_filter = st.sidebar.slider(
            "Filter by Sales Amount ($)",
            min_value=min_sales,
            max_value=max_sales,
            value=(min_sales, max_sales),
            step=10.0,
            format="$%f",
            help="Drag the sliders to filter data based on the sales amount. The charts will update automatically."
        )
        
        categories = ["All"] + sorted(df['Category'].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Product Category", categories)

        filtered_df = df[(df['Sales'] >= sales_filter[0]) & (df['Sales'] <= sales_filter[1])]
        if selected_category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == selected_category]

        category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        category_sales['Percentage'] = category_sales['Sales'] / category_sales['Sales'].sum() if not category_sales.empty else 0

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sales by Category (Bar Chart)")
            st.altair_chart(alt.Chart(category_sales).mark_bar().encode(
                x=alt.X('Category', sort='-y', axis=alt.Axis(labelAngle=0)),
                y='Sales',
                color=alt.Color('Category', scale=category_scale),
            ).properties(height=500), use_container_width=True)

        with col2:
            st.subheader("Sales by Category (Pie Chart)")
            base = alt.Chart(category_sales).encode(
                theta=alt.Theta(field="Sales", type="quantitative", stack=True),
                color=alt.Color(field="Category", type="nominal", scale=category_scale),
                order=alt.Order("Category", sort="ascending"),
                tooltip=['Category', 'Sales', alt.Tooltip('Percentage:Q', format='.1%')]
            )
            
            pie = base.mark_arc(outerRadius=180)
            text = base.mark_text(radius=210, size=18, color='black', fontWeight='bold').encode(
                text=alt.Text(field="Percentage", type="quantitative", format=".1%")
            )
            
            st.altair_chart((pie + text).properties(height=600), use_container_width=True)

    elif view_selection == "Bar Chart + Scatter Plot":
        st.title("Interactive View: Bar Chart + Scatter Plot")
        
        st.markdown("""
        ### How to Navigate this View
        * **Filter by Category:** Click on a bar in the **Bar Chart** (left) to filter the **Scatter Plot** (right) by that category.
        * **Reset Filter:** Click on the chart background or the same bar again to show all categories.
        * **Interactive Scatter Plot:** Use your mouse wheel to **zoom** and click-and-drag to **pan** around the scatter plot.
        * **Tooltips:** Hover over any data point to see specific details like Unit Price, Quantity, and Product Category.
        """)

        click_selection = alt.selection_point(fields=['Category'], name="CategoryClick")
        category_sales_all = df.groupby('Category')['Sales'].sum().reset_index()
        
        bar = alt.Chart(category_sales_all).mark_bar().encode(
            x=alt.X('Category', axis=alt.Axis(labelAngle=0)),
            y='Sales',
            color=alt.condition(click_selection, alt.Color('Category:N', scale=category_scale), alt.value('lightgray'))
        ).add_params(click_selection).properties(width=300, height=500, title="Select a Category")

        scatter = alt.Chart(df).mark_circle(size=80).encode(
            x=alt.X('Unit Price:Q', title="Unit Price ($)"),
            y=alt.Y('Quantity:Q', title="Quantity"),
            color=alt.Color('Category:N', scale=category_scale)
        ).transform_filter(click_selection).properties(width=700, height=500, title="Price vs. Quantity").interactive()

        st.altair_chart(alt.hconcat(bar, scatter, spacing=50), use_container_width=True)

    elif view_selection == "Line Chart + Histogram":
        st.title("Interactive View: Line Chart + Histogram")
        
        st.markdown("""
        ### How to Navigate this View
        * **Filter by Time:** Click and drag your mouse across the **Line Chart** (top) to create a **selection window** (brush).
        * **Analyze Period:** The **Histogram** (bottom) will update to show the quantity distribution for the selected time period.
        * **Move Selection:** Click and drag the highlighted box to see how distribution changes over different years.
        * **Reset:** Click once anywhere on the line chart background to remove the selection filter.
        """)

        brush = alt.selection_interval(encodings=['x'])
        df_monthly = df.resample('ME', on='Order Date')['Sales'].sum().reset_index()

        line = alt.Chart(df_monthly).mark_line(point=True).encode(
            x=alt.X('Order Date:T', title="Month-Year", axis=alt.Axis(format='%b %Y', labelAngle=-45)),
            y=alt.Y('Sales:Q', title="Total Sales ($)")
        ).add_params(brush).properties(width=1000, height=350, title="Sales Over Time (Select Period)")

        hist = alt.Chart(df).mark_bar(binSpacing=0).encode(
            x=alt.X('Quantity:Q', bin=alt.Bin(maxbins=14), title="Quantity Range"),
            y=alt.Y('count()', title="Number of orders (frequency)"),
            color=alt.value("#66b3ff"),
            tooltip=[
                alt.Tooltip('Quantity:Q', bin=True, title='Quantity Interval'),
                alt.Tooltip('count()', title='Number of Orders')
            ]
        ).transform_filter(brush).properties(width=1000, height=350, title="Quantity Distribution")

        st.altair_chart(line & hist, use_container_width=True)

    elif view_selection == "Pie Chart + Bar Chart":
        st.title("Interactive View: Pie Chart + Bar Chart")
        
        st.markdown("""
        ### How to Navigate this View
        * **Select Category:** Click on a slice of the **Pie Chart** (left) to filter the **Regional Bar Chart** (right).
        * **Unified Colors:** Notice that the regional bars will match the color of the selected category for easy identification.
        * **Reset:** Click on the chart background or the same slice again to show data for all categories.
        * **Details:** Hover over any chart element to see exact sales figures and percentage contributions.
        """)
        
        # Define the selection
        pie_selection = alt.selection_point(fields=['Category'], name="PieSelect", empty=True)
        
        category_sales = df.groupby('Category')['Sales'].sum().reset_index()
        category_sales['Percentage'] = category_sales['Sales'] / category_sales['Sales'].sum()

        base = alt.Chart(category_sales).encode(
            theta=alt.Theta(field="Sales", type="quantitative", stack=True),
            color=alt.Color(field="Category", type="nominal", scale=category_scale),
            order=alt.Order("Category", sort="ascending"),
            tooltip=['Category', 'Sales', alt.Tooltip('Percentage:Q', format='.1%')]
        )

        pie = base.mark_arc(outerRadius=160)
        text = base.mark_text(radius=190, size=18, color='black', fontWeight='bold').encode(
            text=alt.Text(field="Percentage", type="quantitative", format=".1%")
        )

        # Add selection and opacity condition to the layered chart
        pie_chart = (pie + text).add_params(
            pie_selection
        ).encode(
            opacity=alt.condition(pie_selection, alt.value(1), alt.value(0.3))
        ).properties(width=400, height=500, title="Sales by Category")

        # Pre-group data for the regional chart
        region_df = df.groupby(['Category', 'Region'])['Sales'].sum().reset_index()

        region_chart = alt.Chart(region_df).mark_bar().encode(
            x=alt.X('Region:N', title="Region"),
            y=alt.Y('Sales:Q', title="Total Sales ($)"),
            color=alt.Color('Category:N', scale=category_scale, legend=None),
            tooltip=['Category', 'Region', 'Sales']
        ).transform_filter(
            pie_selection
        ).properties(width=600, height=500, title="Sales by Region")

        # Use hconcat and resolve color scales
        combined_chart = alt.hconcat(pie_chart, region_chart, spacing=80).resolve_scale(color='independent')
        st.altair_chart(combined_chart, use_container_width=True)

    elif view_selection == "Geographic View + Scatter Plot":
        st.title("Interactive View: Geographic Map + Scatter Plot")
        
        st.markdown("""
        ### How to Navigate this View
        * **Select a State:** Click on any **State** on the map to filter the **Scatter Plot** below.
        * **Geographic Trends:** The map is colored by total sales volume—darker blue represents higher sales.
        * **Analyze State Data:** The scatter plot shows the relationship between Quantity and Sales specifically for your selected state.
        * **Reset Map:** Click on the ocean/background of the map to clear the filter and show all national data.
        """)

        # Map state names to IDs for the US TopoJSON (Standard ANSI)
        state_to_id = {
            'Alabama': 1, 'Alaska': 2, 'Arizona': 4, 'Arkansas': 5, 'California': 6, 'Colorado': 8,
            'Connecticut': 9, 'Delaware': 10, 'District of Columbia': 11, 'Florida': 12, 'Georgia': 13,
            'Hawaii': 15, 'Idaho': 16, 'Illinois': 17, 'Indiana': 18, 'Iowa': 19, 'Kansas': 20,
            'Kentucky': 21, 'Louisiana': 22, 'Maine': 23, 'Maryland': 24, 'Massachusetts': 25,
            'Michigan': 26, 'Minnesota': 27, 'Mississippi': 28, 'Missouri': 29, 'Montana': 30,
            'Nebraska': 31, 'Nevada': 32, 'New Hampshire': 33, 'New Jersey': 34, 'New Mexico': 35,
            'New York': 36, 'North Carolina': 37, 'North Dakota': 38, 'Ohio': 39, 'Oklahoma': 40,
            'Oregon': 41, 'Pennsylvania': 42, 'Rhode Island': 44, 'South Carolina': 45, 'South Dakota': 46,
            'Tennessee': 47, 'Texas': 48, 'Utah': 49, 'Vermont': 50, 'Virginia': 51, 'Washington': 53,
            'West Virginia': 54, 'Wisconsin': 55, 'Wyoming': 56
        }
        
        map_df = df.copy()
        map_df['id'] = map_df['State'].map(state_to_id)
        
        # Aggregate data for map
        state_sales = map_df.groupby(['id', 'State'])['Sales'].sum().reset_index()

        state_selection = alt.selection_point(fields=['State'], name="StateSelect", empty=True)

        states_geo = alt.topo_feature('https://cdn.jsdelivr.net/npm/vega-datasets@v1.29.0/data/us-10m.json', 'states')

        map_base = alt.Chart(states_geo).mark_geoshape().encode(
            color=alt.condition(state_selection, 
                                alt.Color('Sales:Q', scale=alt.Scale(scheme='blues'), title="Total Sales ($)"), 
                                alt.value('lightgray')),
            tooltip=['State:N', 'Sales:Q']
        ).transform_lookup(
            lookup='id',
            from_=alt.LookupData(state_sales, 'id', ['State', 'Sales'])
        ).add_params(state_selection).properties(width=800, height=450, title="Sales by State")

        scatter = alt.Chart(df).mark_circle(size=80).encode(
            x=alt.X('Quantity:Q', title="Quantity"),
            y=alt.Y('Sales:Q', title="Sales ($)"),
            color=alt.Color('Category:N', scale=category_scale),
            tooltip=['Product Name', 'State', 'Sales', 'Quantity']
        ).transform_filter(state_selection).properties(width=800, height=400, title="Sales vs. Quantity for Selected State").interactive()

        st.altair_chart(map_base & scatter, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
