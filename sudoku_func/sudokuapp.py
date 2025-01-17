import streamlit as st
import pymysql
import pandas as pd
import ast
from solver import candi_init, candi_update

st.title('S.S.S (Solve Sudoku with Strategy)')


st.write('Select strategies from **SIDEBAR**. A higher number indicates greater difficulty. You may proceed without selecting any options.')

st.sidebar.title('Select Strategy')
str_checkboxes = {
    "rule_1_hidden_single": st.sidebar.checkbox("rule 1. hidden single"),
    "rule_2_naked_pair": st.sidebar.checkbox("rule 2. naked pair"),
    "rule_3_naked_triple": st.sidebar.checkbox("rule 3. naked triple"),
    "rule_4_hidden_pair": st.sidebar.checkbox("rule 4. hidden pair"),
}

querytext_str='''
SELECT * 
FROM sudoku_data 
WHERE JSON_EXTRACT(strategy, '$.rule_0_single_candi') >= 1 
'''
for str, is_checked in str_checkboxes.items():
    if str_checkboxes[str]:
        querytext_str+=f" AND JSON_EXTRACT(strategy, '$.{str}') >= 1"

querytext_str+='  ORDER BY RAND() limit 1;'

call_by_str=st.sidebar.button('Load with Selected Strategies')

st.sidebar.title('Select with ID')
sudoku_id = st.sidebar.text_input("ID")
call_by_id=st.sidebar.button('Load with ID')

querytext_id=f'''
SELECT * 
FROM sudoku_data 
WHERE ID={sudoku_id};
'''

print(querytext_id)
print(call_by_id)

probdata = None

#session_state
if 'probdata' not in st.session_state:
    st.session_state.probid = None
    st.session_state.probdata = None
    st.session_state.probdata_converted = []
    st.session_state.answer = None
if 'candidates' not in st.session_state:
    st.session_state.candidates = [[set() for _ in range(9)] for _ in range(9)]

if call_by_str:
    with open('password.pw', 'r') as pw_file:
        db_password = pw_file.read().strip()

    database_name = 'sudoku_db'

    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password=db_password,
            database=database_name,
            charset='utf8mb3'
        )
        st.success("Connected to the database successfully!")

        with connection.cursor() as cursor:
            query = querytext_str
            cursor.execute(query)
            probid, probdata, strategy, answer, level, timestamp = cursor.fetchone()
            st.session_state.probid = probid
            st.session_state.probdata = probdata
            st.session_state.answer = answer
            st.session_state.probdata_converted = ast.literal_eval(probdata)
            # print(type(st.session_state.probdata_converted[2][4]))
            for i in range(9):
                for j in range(9):
                    if st.session_state.probdata_converted[i][j] == 0:
                        st.session_state.probdata_converted[i][j] = ''

    except Exception as e:
        st.error(f"An error occurred while connecting to the database: {e}")

    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if call_by_id:
    # with open('password.pw', 'r') as pw_file:
    #     db_password = pw_file.read().strip()
    #왜 주석 처리가 안되는가? 

    database_name = 'sudoku_db'

    try:
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password=db_password,
            database=database_name,
            charset='utf8mb3'
        )
        st.success("Connected to the database successfully!")

        with connection.cursor() as cursor:
            query = querytext_id
            cursor.execute(query)
            probid, probdata, strategy, answer, level, timestamp = cursor.fetchone()
            st.session_state.probid = probid
            st.session_state.probdata = probdata
            st.session_state.answer = answer
            st.session_state.probdata_converted = ast.literal_eval(probdata)
            # print(type(st.session_state.probdata_converted[2][4]))
            for i in range(9):
                for j in range(9):
                    if st.session_state.probdata_converted[i][j] == 0:
                        st.session_state.probdata_converted[i][j] = ''

    except Exception as e:
        st.error(f"An error occurred while connecting to the database: {e}\n\n**Some ID might not exits**")

    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

# HTML for the Sudoku table
def generate_sudoku_table(data, selected_row=None, selected_col=None):
    table_html = '<table class="sudoku-table">'
    for i, row in enumerate(data):
        table_html += '<tr>'
        for j, cell in enumerate(row):
            # selection  >> cell class 
            cell_class = ''
            if selected_row is not None and selected_col is not None:
                if i == selected_row - 1 and j == selected_col - 1:
                    # print("if 1", i,j,selected_row, selected_col)
                    cell_class = 'selected-cell'
                elif i == selected_row - 1:
                    # print("elif 1", i,j,selected_row, selected_col)
                    cell_class = 'selected-row'
                elif j == selected_col - 1:
                    # print("elif 2", i,j, selected_row, selected_col)
                    cell_class = 'selected-col'
            
            main_number = f"<div class='main-number'>{cell}</div>" if cell else ""
            candidates = "<div class='candidates'></div>"
            if not cell:  # Only show candidates if cell is empty
                for num in range(1, 10):
                    if num in st.session_state.candidates[i][j]:
                        candidates += f"<span>{num}</span>"
                    else:
                        candidates += "<span></span>"
            candidates += "</div>"
            table_html += f"<td class='{cell_class}'>{main_number}{candidates}</td>"
        table_html += '</tr>'
    table_html += '</table>'
    return table_html


# CSS for styling the Sudoku table
st.markdown(
    """
    <style>
    .sudoku-table {
        border-collapse: collapse;
        margin: auto;
    }
    .sudoku-table td {
        width: 60px;
        height: 60px;
        border: 1px solid #999;
        position: relative;
        text-align: center;
        vertical-align: middle;
    }
    .main-number {
        font-size: 24px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .candidates {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        font-size: 10px;
        padding: 2px;
    }
    /* Add specific styles for selected cells */
    .sudoku-table td.selected-row {
        background-color: #E3FFFB !important;
    }
    .sudoku-table td.selected-col {
        background-color: #E3FFFB !important;
    }
    .sudoku-table td.selected-cell {
        background-color: #CCFFF8 !important;
    }
    /* 3x3 grid borders */
    .sudoku-table tr:nth-child(3n) td {
        border-bottom: 2px solid #000;
    }
    .sudoku-table td:nth-child(3n) {
        border-right: 2px solid #000;
    }
    .sudoku-table {
        border: 2px solid #000;
    }
    </style>
    """,
    unsafe_allow_html=True
)


if st.session_state.probdata:
    if 'selected_row' not in st.session_state:
        st.session_state.selected_row = None
    if 'selected_col' not in st.session_state:
        st.session_state.selected_col = None
    
    st.subheader(f"Current sudoku ID: {st.session_state.probid}")
    answercheck=st.button('Check answer')
    if answercheck:
        if st.session_state.probdata:
            # Convert answer string to list
            answer_converted = ast.literal_eval(st.session_state.answer)
            
            # Convert empty strings back to numbers for comparison
            current_answer = [[int(cell) if cell != '' else 0 for cell in row] 
                            for row in st.session_state.probdata_converted]
            
            # Compare the lists
            if current_answer == answer_converted:
                st.success("Good job!")
            else:
                st.error("Your answer does not match with answer data. Please check your answer again")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.selected_row = st.selectbox('row', options=range(1, 10))
        # print(st.session_state.selected_row)
    with col2:
        st.session_state.selected_col = st.selectbox('column', options=range(1, 10))
        # print(st.session_state.selected_col)
    
    
    answerbtncol1,answerbtncol2=st.columns(2)
    with answerbtncol1:
        st.subheader('Answer input')
    with answerbtncol2:
        ansclr=st.button('Del')
        if ansclr:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = ''
    anscol2,anscol3,anscol4,anscol5,anscol6,anscol7,anscol8,anscol9,anscol10= st.columns(9)
    with anscol2:
        ansin1=st.button('1')
        if ansin1:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 1
                
    with anscol3:
        ansin2=st.button('2')
        if ansin2:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 2
    with anscol4:
        ansin3=st.button('3')
        if ansin3:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 3
    with anscol5:
        ansin4=st.button('4')
        if ansin4:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 4
    with anscol6:
        ansin5=st.button('5')
        if ansin5:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 5
    with anscol7:
        ansin6=st.button('6')
        if ansin6:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 6
    with anscol8:
        ansin7=st.button('7')
        if ansin7:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 7
    with anscol9:
        ansin8=st.button('8')
        if ansin8:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 8
    with anscol10:
        ansin9=st.button('9')
        if ansin9:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                st.session_state.probdata_converted[row_idx][col_idx] = 9
    

    candibtncol1,candibtncol2=st.columns(2)
    with candibtncol1:
        st.subheader('Candidates input')
    with candibtncol2:
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            fill_candi=st.button('Fill candidates')
            if fill_candi:
                if st.session_state.probdata:
                    # Convert empty strings back to 0 for candi_init function
                    temp_probdata = [[0 if cell == '' else cell for cell in row] for row in st.session_state.probdata_converted]
                    # Run candi_init function
                    st.session_state.candidates = candi_init(temp_probdata)

        with subcol2:
            update_candi=st.button('Update candidates')
            if update_candi:
                if st.session_state.probdata:
                    # Convert empty strings back to 0 for candi_init function
                    temp_probdata = [[0 if cell == '' else cell for cell in row] for row in st.session_state.probdata_converted]
                    # Run candi_init function
                    st.session_state.candidates = candi_update(temp_probdata,st.session_state.candidates)
    
    

    candicol2,candicol3,candicol4,candicol5,candicol6,candicol7,candicol8,candicol9,candicol10 = st.columns(9)
    with candicol2:
        candiin1=st.button('c1')
        if candiin1:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 1 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(1)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(1)
    with candicol3:
        candiin2=st.button('c2')
        if candiin2:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 2 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(2)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(2)
    with candicol4:
        candiin3=st.button('c3')
        if candiin3:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 3 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(3)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(3)
    with candicol5:
        candiin4=st.button('c4')
        if candiin4:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 4 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(4)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(4)
    with candicol6:
        candiin5=st.button('c5')
        if candiin5:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 5 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(5)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(5)
    with candicol7:
        candiin6=st.button('c6')
        if candiin6:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 6 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(6)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(6)
    with candicol8:
        candiin7=st.button('c7')
        if candiin7:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 7 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(7)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(7)
    with candicol9:
        candiin8=st.button('c8')
        if candiin8:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 8 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(8)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(8)
    with candicol10:
        candiin9=st.button('c9')
        if candiin9:
            if st.session_state.selected_row and st.session_state.selected_col:
                row_idx = st.session_state.selected_row - 1
                col_idx = st.session_state.selected_col - 1
                # Toggle candidate number
                if 9 in st.session_state.candidates[row_idx][col_idx]:
                    st.session_state.candidates[row_idx][col_idx].remove(9)
                else:
                    st.session_state.candidates[row_idx][col_idx].add(9)
    
    # Use the stored converted data directly
    sudoku_table_html = generate_sudoku_table(st.session_state.probdata_converted, st.session_state.selected_row, 
    st.session_state.selected_col)
    st.markdown(sudoku_table_html, unsafe_allow_html=True)
    
    
    

    