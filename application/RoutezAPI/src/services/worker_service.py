from multiprocessing import Process, Queue
import traceback

def _worker_target(queue, algoritmo, dist_matrix_np, pois_salvos):
    """
    This function runs in a separate process.
    It executes the algorithm and puts the result into the queue.
    """
    try:
        best_path, min_distance, resultadoDasMetricas = algoritmo.executar(dist_matrix_np, pois_salvos)
        queue.put((best_path, min_distance, resultadoDasMetricas, None))
    except Exception as e:
        # Pass exception details back to the main process
        error_info = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        queue.put((None, None, None, error_info))

def execute_algorithm_in_worker(algoritmo, dist_matrix_np, pois_salvos):
    """
    Executes the algorithm in a separate process and waits for the result.
    """
    q = Queue()
    
    # Using Process to run the algorithm in a separate process
    process = Process(target=_worker_target, args=(q, algoritmo, dist_matrix_np, pois_salvos))
    process.start()
    
    # Get the result from the queue (this will block until the worker is done)
    result = q.get()
    
    process.join() # Ensure the process has finished
    
    best_path, min_distance, resultadoDasMetricas, error_info = result

    if error_info:
        print(f"Ocorreu uma exceção no worker: {error_info['type']} - {error_info['message']}")
        print(error_info['traceback'])
        raise Exception(f"Erro no worker ao executar o algoritmo: {error_info['message']}")

    return best_path, min_distance, resultadoDasMetricas
