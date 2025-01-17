import copy
import pymysql

def candi_init(probdata):
    # init
    candilist = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]

    #remove
    for i in range(9):
        for j in range(9):
            if probdata[i][j] != 0:
                #empty
                candilist[i][j] = set()
                num = probdata[i][j]
                # row, column check
                for k in range(9):
                    candilist[i][k].discard(num) 
                    candilist[k][j].discard(num) 
                
                #box check
                start_row, start_col = 3 * (i // 3), 3 * (j // 3)
                for r in range(start_row, start_row + 3):
                    for c in range(start_col, start_col + 3):
                        candilist[r][c].discard(num)  

    return candilist

def candi_update(probdata, candilist):
    for i in range(9):
        for j in range(9):
            if probdata[i][j] != 0:
                #empty
                candilist[i][j] = set()
                num = probdata[i][j]
                # row, column check
                for k in range(9):
                    candilist[i][k].discard(num) 
                    candilist[k][j].discard(num) 
                
                #box check
                start_row, start_col = 3 * (i // 3), 3 * (j // 3)
                for r in range(start_row, start_row + 3):
                    for c in range(start_col, start_col + 3):
                        candilist[r][c].discard(num)  

    return candilist

def rule_0_single_candi(probdata, candilist):
    for i in range(9):
        for j in range(9):
            # single_candi
            if len(candilist[i][j]) == 1:
                num = candilist[i][j].pop()
                probdata[i][j] = num
                # print("pop check", i, j , num, probdata[i][j],candilist[i][j] )

                row = probdata[i]
                col = [probdata[x][j] for x in range(9)]
                box = [
                    probdata[x][y]
                    for x in range((i // 3) * 3, (i // 3) * 3 + 3)
                    for y in range((j // 3) * 3, (j // 3) * 3 + 3)
                ]
                
                if row.count(num) > 1 or col.count(num) > 1 or box.count(num) > 1:
                    print("Invalid Problem")
                    return probdata, candilist

                # candi_update
                candilist = candi_update(probdata, candilist)
                # print("inter candi check", candilist)
                
                # probdata 0, candi==set() =>Invalid
                for x in range(9):
                    for y in range(9):
                        if probdata[x][y] == 0 and len(candilist[x][y]) == 0:
                            print("Invalid Problem")
                            return probdata, candilist
    
    # candi_update
    candilist = candi_update(probdata, candilist)

    return probdata, candilist



def rule_1_hidden_single(candilist):
    
    for i in range(9):
        for j in range(9):
            if candilist[i][j] != set():
                for num in list(candilist[i][j]): #for each elements in listified set
                    # row check
                    row_count = sum(1 for col in range(9) if num in candilist[i][col])
                    if row_count == 1:
                        candilist[i][j] = {num}
                        break

                    # column check
                    col_count = sum(1 for row in range(9) if num in candilist[row][j])
                    if col_count == 1:
                        candilist[i][j] = {num}
                        break

                    # box check
                    box_row_start = (i // 3) * 3
                    box_col_start = (j // 3) * 3
                    box_count = sum(
                        1
                        for r in range(box_row_start, box_row_start + 3)
                        for c in range(box_col_start, box_col_start + 3)
                        if num in candilist[r][c]
                    )
                    if box_count == 1:
                        candilist[i][j] = {num}
                        break

    return candilist

def rule_2_naked_pair(candilist):

    for i in range(9):
        for j in range(9):
            if len(candilist[i][j]) == 2:
                # 현재 셀의 후보 숫자
                pair = candilist[i][j]

                # 행(row), 열(col), 박스(box) 정의
                row = [candilist[i][k] for k in range(9)]
                col = [candilist[k][j] for k in range(9)]
                box_row_start = (i // 3) * 3
                box_col_start = (j // 3) * 3
                box = [candilist[box_row_start + k][box_col_start + l] for k in range(3) for l in range(3)]

                # **행(row) 처리**
                if row.count(pair) == 2:  # Naked Pair가 행에 존재
                    for k in range(9):
                        if candilist[i][k] != pair:  # Naked Pair가 아닌 셀만 처리
                            candilist[i][k] -= pair

                # **열(col) 처리**
                if col.count(pair) == 2:  # Naked Pair가 열에 존재
                    for k in range(9):
                        if candilist[k][j] != pair:  # Naked Pair가 아닌 셀만 처리
                            candilist[k][j] -= pair

                # **박스(box) 처리**
                if box.count(pair) == 2:  # Naked Pair가 박스에 존재
                    for k in range(3):
                        for l in range(3):
                            row_idx = box_row_start + k
                            col_idx = box_col_start + l
                            if candilist[row_idx][col_idx] != pair:  # Naked Pair가 아닌 셀만 처리
                                candilist[row_idx][col_idx] -= pair

    return candilist


def rule_3_naked_triple(candilist):
    for i in range(9):
        for j in range(9):
            # Row, Column, Box 정의
            row = [candilist[i][k] for k in range(9)]
            col = [candilist[k][j] for k in range(9)]
            box_row_start = (i // 3) * 3
            box_col_start = (j // 3) * 3
            box = [
                candilist[box_row_start + k][box_col_start + l]
                for k in range(3)
                for l in range(3)
            ]
            
            # Naked Triple 탐색
            for k in range(9 - 2):
                for l in range(k + 1, 9 - 1):
                    for m in range(l + 1, 9):
                        # Row 처리
                        row_union_set = row[k] | row[l] | row[m]
                        if len(row_union_set) == 3 and len(row[k]) != 0 and len(row[l]) != 0 and len(row[m]) != 0:
                            for n in range(9):
                                if n not in [k, l, m]:
                                    candilist[i][n] -= row_union_set

                        # Column 처리
                        col_union_set = col[k] | col[l] | col[m]
                        if len(col_union_set) == 3 and len(col[k]) != 0 and len(col[l]) != 0 and len(col[m]) != 0:
                            for n in range(9):
                                if n not in [k, l, m]:
                                    candilist[n][j] -= col_union_set

                        # Box 처리
                        box_union_set = box[k] | box[l] | box[m]
                        if len(box_union_set) == 3 and len(box[k]) != 0 and len(box[l]) != 0 and len(box[m]) != 0:
                            for n in range(9):
                                if n not in [k, l, m]:
                                    row_idx = box_row_start + (n // 3)
                                    col_idx = box_col_start + (n % 3)
                                    candilist[row_idx][col_idx] -= box_union_set

    return candilist


def rule_4_hidden_pair(candilist):
    for i in range(9):
        for j in range(9):
            # Row 처리
            row = [candilist[i][k] for k in range(9)]
            candi_posi_row = {}
            for k, candi_set in enumerate(row):
                for num in candi_set:
                    if num not in candi_posi_row:
                        candi_posi_row[num] = []
                    candi_posi_row[num].append(k)
            
            for num1 in candi_posi_row:
                for num2 in candi_posi_row:
                    if num1 < num2:
                        posi1 = set(candi_posi_row[num1])
                        posi2 = set(candi_posi_row[num2])
                        
                        if posi1 == posi2 and len(posi1 & posi2) == 2:  # Hidden Pair 발견
                            for l in posi1:
                                candilist[i][l] = {num1, num2}  # candilist를 직접 수정
            
            # Column 처리
            col = [candilist[k][j] for k in range(9)]
            candi_posi_col = {}
            for k, candi_set in enumerate(col):
                for num in candi_set:
                    if num not in candi_posi_col:
                        candi_posi_col[num] = []
                    candi_posi_col[num].append(k)
            
            for num1 in candi_posi_col:
                for num2 in candi_posi_col:
                    if num1 < num2:
                        posi1 = set(candi_posi_col[num1])
                        posi2 = set(candi_posi_col[num2])
                        
                        if posi1 == posi2 and len(posi1 & posi2) == 2:  # Hidden Pair 발견
                            for l in posi1:
                                candilist[l][j] = {num1, num2}  # candilist를 직접 수정
            
            # Box 처리
            box_row_start = (i // 3) * 3
            box_col_start = (j // 3) * 3
            box = [candilist[box_row_start + k][box_col_start + l] for k in range(3) for l in range(3)]
            candi_posi_box = {}
            for k, candi_set in enumerate(box):
                for num in candi_set:
                    if num not in candi_posi_box:
                        candi_posi_box[num] = []
                    candi_posi_box[num].append(k)
            
            for num1 in candi_posi_box:
                for num2 in candi_posi_box:
                    if num1 < num2:
                        posi1 = set(candi_posi_box[num1])
                        posi2 = set(candi_posi_box[num2])
                        
                        if posi1 == posi2 and len(posi1 & posi2) == 2:  # Hidden Pair 발견
                            for l in posi1:
                                row_idx = box_row_start + (l // 3)
                                col_idx = box_col_start + (l % 3)
                                candilist[row_idx][col_idx] = {num1, num2}  # candilist를 직접 수정

    return candilist

def solve(probdata):
    original_probdata = copy.deepcopy(probdata)
    rule_counts = {
        "rule_0_single_candi": 0,
        "rule_1_hidden_single": 0,
        "rule_2_naked_pair": 0,
        "rule_3_naked_triple":0,
        "rule_4_hidden_pair":0
    }

    max_iterations = 2000
    iteration_count = 0
    stalled = False
    candilist = candi_init(probdata)
    
    while iteration_count < max_iterations:
        iteration_count += 1
    
        # Check invalid candidates (empty sets)
        if any(len(candilist[i][j]) == 0 and probdata[i][j] == 0 for i in range(9) for j in range(9)):
            return "Invalid Problem", original_probdata, rule_counts, probdata

        # Check invalid probdata
        for i in range(9):
            for j in range(9):
                row = [candilist[i][k] for k in range(9)]
                col = [candilist[k][j] for k in range(9)]
                box_row_start = (i // 3) * 3
                box_col_start = (j // 3) * 3
                box = [
                    candilist[box_row_start + k][box_col_start + l]
                    for k in range(3)
                    for l in range(3)
                ]
                #row check
                if row.count(probdata[i][j])>1:
                    return "Invalid Problem", original_probdata, rule_counts, probdata
                
                #col check
                if col.count(probdata[i][j])>1:
                    return "Invalid Problem", original_probdata, rule_counts, probdata
                
                #box check
                if box.count(probdata[i][j])>1:
                    return "Invalid Problem", original_probdata, rule_counts, probdata

        #deepcopy for count befor apply
        prev_probdata = copy.deepcopy(probdata)
        prev_candilist = copy.deepcopy(candilist)

        # Apply rules_0
        probdata, candilist = rule_0_single_candi(probdata, candilist)

        if all(0 not in row for row in probdata):
            rule_counts["rule_0_single_candi"] += 1
            return "Solved", original_probdata, rule_counts, probdata

        if probdata != prev_probdata or candilist != prev_candilist:
            rule_counts["rule_0_single_candi"] += 1
            stalled = False
            continue

        #deepcopy for count befor apply
        prev_probdata = copy.deepcopy(probdata)
        prev_candilist = copy.deepcopy(candilist)

        # Apply rules_1
        candilist = rule_1_hidden_single(candilist)

        if all(0 not in row for row in probdata):
            rule_counts["rule_1_hidden_single"] += 1
            return "Solved", original_probdata, rule_counts, probdata

        if probdata != prev_probdata or candilist != prev_candilist:
            rule_counts["rule_1_hidden_single"] += 1
            stalled = False
            continue
        
        #deepcopy for count befor apply
        prev_probdata = copy.deepcopy(probdata)
        prev_candilist = copy.deepcopy(candilist)

        # Apply rules_2
        candilist = rule_2_naked_pair(candilist)

        if all(0 not in row for row in probdata):
            rule_counts["rule_2_naked_pair"] += 1
            return "Solved", original_probdata, rule_counts, probdata

        if probdata != prev_probdata or candilist != prev_candilist:
            rule_counts["rule_2_naked_pair"] += 1
            stalled = False
            continue

        #deepcopy for count befor apply
        prev_probdata = copy.deepcopy(probdata)
        prev_candilist = copy.deepcopy(candilist)

        # Apply rules_3
        candilist = rule_3_naked_triple(candilist)

        if all(0 not in row for row in probdata):
            rule_counts["rule_3_naked_triple"] += 1
            return "Solved", original_probdata, rule_counts, probdata

        if probdata != prev_probdata or candilist != prev_candilist:
            rule_counts["rule_3_naked_triple"] += 1
            stalled = False
            continue

        #deepcopy for count befor apply
        prev_probdata = copy.deepcopy(probdata)
        prev_candilist = copy.deepcopy(candilist)

        # Apply rules_4
        candilist = rule_4_hidden_pair(candilist)

        if all(0 not in row for row in probdata):
            rule_counts["rule_4_hidden_pair"] += 1
            return "Solved", original_probdata, rule_counts, probdata

        if probdata != prev_probdata or candilist != prev_candilist:
            rule_counts["rule_4_hidden_pair"] += 1
            stalled = False
            continue

        if stalled:
            print("Stuck: Unable to solve further.")
            return "Unable to Solve", original_probdata, rule_counts, probdata

        stalled = True

    print("Iteration limit reached. Exiting.")
    return "Unable to Solve", original_probdata, rule_counts, probdata





# probdata = [[0,7,2,0,0,0,5,0,0],
#             [0,3,1,0,0,7,6,0,0],
#             [0,0,9,0,1,3,0,2,7],
#             [4,0,0,0,0,8,0,0,2],
#             [0,2,8,5,6,0,0,7,4],
#             [7,6,3,0,0,9,1,8,0],
#             [3,0,0,0,4,0,0,1,8],
#             [0,0,0,8,3,0,0,0,0],
#             [2,8,4,1,9,6,7,5,3]]






# print(solve(probdata))

 
# [[6, 7, 2, 9, 8, 4, 5, 3, 1], 
#  [8, 3, 1, 2, 5, 7, 6, 4, 9], 
#  [5, 4, 9, 6, 1, 3, 8, 2, 7], 
#  [4, 1, 5, 3, 7, 8, 9, 6, 2], 
#  [9, 2, 8, 5, 6, 1, 3, 7, 4], 
#  [7, 6, 3, 4, 2, 9, 1, 8, 5], 
#  [3, 9, 6, 7, 4, 5, 2, 1, 8], 
#  [1, 5, 7, 8, 3, 2, 4, 9, 6], 
#  [2, 8, 4, 1, 9, 6, 7, 5, 3]]





# probdata = [
#     [0, 0, 5, 0, 0, 2, 0, 0, 8], 
#     [0, 0, 3, 0, 4, 0, 7, 0, 0], 
#     [0, 0, 0, 9, 8, 6, 3, 0, 4], 
#     [5, 4, 0, 0, 7, 0, 9, 6, 0], 
#     [0, 0, 0, 0, 9, 0, 0, 0, 2], 
#     [0, 0, 0, 6, 0, 0, 0, 0, 0], 
#     [0, 9, 8, 0, 0, 3, 0, 7, 1], 
#     [3, 5, 4, 0, 0, 0, 0, 0, 0], 
#     [0, 1, 2, 0, 0, 0, 0, 3, 0]]
# probdata = [
#     [7,2,0,1,9,6,0,8,3], 
#     [0,0,0,2,8,5,0,7,0], 
#     [0,8,0,3,7,4,0,2,0], 
#     [0,0,0,9,4,0,0,6,0], 
#     [1,9,6,5,2,3,8,4,7], 
#     [0,4,0,6,1,0,0,0,0], 
#     [0,3,0,8,0,1,0,9,0], 
#     [0,0,0,7,0,2,0,0,0], 
#     [2,0,0,4,3,9,0,1,8]]

# print(solve(probdata))

# candilist=candi_init(probdata)
# probdata
# candilist

# rule_0_single_candi(probdata,candilist)[1]
# rule_0_single_candi(probdata,candilist)[1]
# rule_1_hidden_single(candilist)
# rule_1_hidden_single(candilist)
# rule_2_naked_pair(candilist)
# rule_2_naked_pair(candilist)
# rule_3_naked_triple(candilist)
# rule_3_naked_triple(candilist)
# rule_0_single_candi(probdata,candilist)[1]
# rule_1_hidden_single(candilist)
# rule_0_single_candi(probdata,candilist)[1]
# rule_0_single_candi(probdata,candilist)[1]
# rule_1_hidden_single(candilist)
# rule_2_naked_pair(candilist)
# rule_3_naked_triple(candilist)
# rule_0_single_candi(probdata,candilist)[1]
# print(rule_4_hidden_pair(candilist))
# print(rule_0_single_candi(probdata,candilist)[1])
# print(rule_1_hidden_single(candilist))
# print(rule_0_single_candi(probdata,candilist)[1])
# print(rule_0_single_candi(probdata,candilist)[1])
# print(rule_0_single_candi(probdata,candilist)[1])
# print(rule_0_single_candi(probdata,candilist)[1])
# print(rule_0_single_candi(probdata,candilist)[1])


# [set(), set(), {4, 5}, set(), set(), set(), {4, 5}, set(), set()], 
# [{3, 4, 6, 9}, {1, 6}, {1, 3, 4, 9}, set(), set(), set(), {1, 4, 6, 9}, set(), {1, 4, 6, 9}], 
# [{5, 6, 9}, set(), {1, 5, 9}, set(), set(), set(), {1, 5, 6, 9}, set(), {1, 5, 6, 9}], 
# [{3, 5, 8}, {5, 7}, {2, 3, 5, 7, 8}, set(), set(), {7, 8}, {1, 2, 3, 5}, set(), {1, 2, 5}], 
# [set(), set(), set(), set(), set(), set(), set(), set(), set()],
# [{3, 5, 8}, set(), {2, 3, 5, 7, 8}, set(), set(), {7, 8}, {2, 3, 5, 9}, {3, 5}, {2, 5, 9}], 
# [{4, 5, 6}, set(), {4, 5, 7}, set(), {5, 6}, set(), {2, 4, 5, 6, 7}, set(), {2, 4, 5, 6}], 
# [{4, 5, 6, 8, 9}, {1, 5, 6}, {1, 4, 5, 8, 9}, set(), {5, 6}, set(), {3, 4, 5, 6}, {3, 5}, {4, 5, 6}],
# [set(), {5, 6, 7}, {5, 7}, set(), set(), set(), {5, 6, 7}, set(), set()]

# [[set(),        set(),      {4,5},      set(),  set(),  set(),  {4,5},          set(),  set()],
# [{3,4,6,9},     {1,6},      {1,3,9},    set(),  set(),  set(),  {1,4,6,9},      set(),  {1,4,6,9}],
# [{5,6,9},       set(),      {1,9},      set(),  set(),  set(),  {1,5,6,9},      set(),  {1,5,6,9}],
# [{3,5},         set(),      {2,3},      set(),  set(),  set(),  {1,2,3,5},      set(),  {1,2,5}],
# [set(),         set(),      set(),      set(),  set(),  set(),  set(),          set(),  set()],
# [{3,5,8},       set(),      {2,3,8},    set(),  set(),  set(),  {2,3,5,9},      {3,5},  {2,5,9}],
# [{4,5,6},       set(),      {4,5,7},    set(),  {5,6},  set(),  {2,4,5,6,7},    set(),  {2,4,5,6}],
# [{4,5,6,8,9},   {1,5,6},    {1,8,9},    set(),  {5,6},  set(),  {3,4,5,6},      {3,5},  {4,5,6}],
# [set(),         {5,6},      {5,7},      set(),  set(),  set(),  {5,6,7},        set(),  set()]]

# [set(),     set(),      {4,5},      set(),  set(),  set(),  {4,5},          set(),  set()],
# [{3,4,6,9}, {1,6},      {1,3,9},    set(),  set(),  set(),  {1,4,6,9},      set(),  {1,4,6,9}],
# [{5,6,9},   set(),      {1,9},      set(),  set(),  set(),  {1,5,6,9},      set(),  {1,5,6,9}],
# [{3,5},     set(),      {2,3},      set(),  set(),  set(),  {1,2,3,5},      set(),  {1,2,5}],
# [set(),     set(),      set(),      set(),  set(),  set(),  set(),          set(),  set()],
# [{3,5,8},   set(),      {2,3,8},    set(),  set(),  set(),  {2,3,5,9},      {3,5},  {2,5,9}],
# [{4,5,6},   set(),      {4,5,7},    set(),  {5,6},  set(),  {2,4,5,6,7},    set(),  {2,4,5,6}],
# [{8,9},     {1,5,6},    {8,9},      set(),  {5,6},  set(),  {3,4,5,6},      {3,5},  {4,5,6}],
# [set(),     {5,6},      {5,7},      set(),  set(),  set(),  {5,6,7},        set(),  set()]