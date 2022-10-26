What the project's going to be about:
    A .exe file that could be executed on the desktop that a user can use to enter their purchases of stocks (maybe crypto). 
    1. The app will keep track of the performance of the portfolio by being able to select the stock and show its performance.
    2. Users could also select more than 1 stock to show as a graph.

Things to implement:
    1. Register/login/logout
    2. Buy/sell/portfolio
    3. Database - users(id,username,hash,)
                - orders(id,user_id,symbol,name,price,shares)
    4. Track(interval,{
                date_of_txn1: {
                    symbol: {price:?, shares:?,}
                },
                date_ of_txn2:{
                    symbol: {price:?, shares:?,}
                },
            }) - Takes in the a time interval arg and a dictionary of txn filtered by date. Returns an array of value of values at equal interval.
    5. Graph(interval,value[]) - Takes interval and array of values of portfolio at  equal interval. Plot the graph out. (CLIENT SIDE?)