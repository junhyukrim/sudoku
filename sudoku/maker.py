import generator  # Importing the generator module
import solver     # Importing the solver module
import pymysql
import json

def maker(num,rules):
    count=0
    print("Generating init sudoku")
    while True:
        # Step 1: Generate a Sudoku puzzle with 30 filled cells
        
        generated_puzzle = generator.generate(num)

        # Step 2: Attempt to solve the generated puzzle
        # print("init sudoku generated. solving ...")
        status, original_puzzle, rule_counts, solved_puzzle = solver.solve(generated_puzzle)
        for idx in range(len(rule_counts)):
            if rules[idx]==1 and list(rule_counts.values())[idx]==0:
                status="Not statisfying requirements"


        # Step 3: Check if the puzzle was solved successfully
        if status == "Solved":
            print("Sudoku puzzle successfully generated on attempt {}!".format(count))
            # print("Generated Puzzle:")
            # for row in original_puzzle:
            #     print(row)
            # print("\nSolved Puzzle:")
            # for row in solved_puzzle:
            #     print(row)
            return count, status, original_puzzle, rule_counts, solved_puzzle

        # If unable to solve, generate a new puzzle and try again
        # print(status, "Unable to solve the generated puzzle. Generating a new one...\n")
        count+=1

def rep_maker_send_to_db(rep,num,rules):
    with open('password.pw', 'r') as pw_file:
        db_password = pw_file.read().strip()
    database_name='sudoku_db'

    connection = pymysql.connect(
        host='localhost', 
        port=3306, 
        user='root', 
        password=db_password, 
        database=database_name, 
        charset='utf8mb3')
    
    insert_counter=0
    for i in range(rep):
        count, status, original_puzzle, rule_counts, solved_puzzle=maker(num,rules)

        if status=='Solved':
            original_puzzle_json = json.dumps(original_puzzle)
            rule_counts_json = json.dumps(rule_counts)
            solved_puzzle_json = json.dumps(solved_puzzle)

            # Prepare values for insertion
            values = [original_puzzle_json, rule_counts_json, solved_puzzle_json]
            
            with connection.cursor() as cur:
                cur.execute( 
                    '''
                    insert into sudoku_data(`problem`,`strategy`,`answer`)
                        values (%s,%s,%s)
                    ''', values
                )
            insert_counter+=1
            print("Successfully sent to {}. total count: {}".format(database_name,insert_counter))


    #db commit
    connection.commit()



rep_maker_send_to_db(10,28,[1,1,1,1,1])