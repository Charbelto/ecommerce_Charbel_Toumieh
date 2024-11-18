from sqlalchemy import text
from sqlalchemy.orm import Session

def analyze_query(db: Session, query):
    """Analyze SQL query performance using EXPLAIN ANALYZE"""
    
    # Get the SQL statement from the SQLAlchemy query
    sql = str(query.statement.compile(compile_kwargs={"literal_binds": True}))
    
    # Execute EXPLAIN ANALYZE
    explain_sql = f"EXPLAIN ANALYZE {sql}"
    result = db.execute(text(explain_sql))
    
    # Return the query execution plan
    return [row[0] for row in result]

def log_slow_queries(db: Session, query, threshold_ms: float = 100):
    """Log queries that take longer than the threshold"""
    import time
    
    start_time = time.time()
    result = query.all()
    execution_time = (time.time() - start_time) * 1000
    
    if execution_time > threshold_ms:
        query_plan = analyze_query(db, query)
        print(f"Slow query detected ({execution_time:.2f}ms):")
        print("Query plan:")
        for line in query_plan:
            print(line)
    
    return result