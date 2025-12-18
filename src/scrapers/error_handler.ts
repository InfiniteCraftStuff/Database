export function withRetries(max_retries: number = 3, delay: number = 100) {
  function decorator<TArgs extends unknown[], TReturn extends Promise<unknown>>(
    func: (...args: TArgs) => TReturn,
  ) {
    async function wrapper(...args: TArgs): Promise<TReturn | null> {
      const for_args_str = `for ${args.join(", ")}` as const;
      const error_log = func.name
        ? (`Error in ${func.name} ${for_args_str}` as const)
        : (`Error ${for_args_str}` as const);
      for (let attempt = 0; attempt <= max_retries; attempt++) {
        try {
          return func(...args);
        } catch (e) {
          if (attempt < max_retries) {
            console.warn(`${error_log}: ${e}. Retrying in ${delay} seconds...`);
            await new Promise((resolve) => setTimeout(resolve, delay));
            continue;
          } else {
            console.error(`${error_log} after ${max_retries} retries: ${e}`);
            return null;
          }
        }
      }
      console.error(`${error_log} after ${max_retries} retries`);
      return null;
    }
    return wrapper;
  }
  return decorator;
}
