using NCalc;

namespace CalculatorBackend.Services;

public class CalculationEngine : ICalculationEngine
{
    public string Evaluate(string expression)
    {
        if (string.IsNullOrWhiteSpace(expression))
        {
            return "0";
        }

        // Remove trailing operators for evaluation
        string evalExpression = expression.TrimEnd('+', '-', '*', '/').Trim();

        if (string.IsNullOrWhiteSpace(evalExpression))
        {
            return "0";
        }

        try
        {
            // NCalc.Core 4.3.0 syntax
            var calc = new Expression(evalExpression);
            var result = calc.Evaluate();

            // Format the result to remove unnecessary decimals
            if (result is double doubleResult)
            {
                // Check for infinity or NaN
                if (double.IsInfinity(doubleResult) || double.IsNaN(doubleResult))
                {
                    return "Error: Invalid result";
                }

                return doubleResult % 1 == 0
                    ? ((long)doubleResult).ToString()
                    : doubleResult.ToString("G");  // "G" format for clean output
            }

            if (result is int || result is long)
            {
                return result.ToString();
            }

            return result?.ToString() ?? "0";
        }
        catch (DivideByZeroException)
        {
            return "Error: Division by zero";
        }
        catch (Exception ex)
        {
            // Log the actual error for debugging
            Console.WriteLine($"Calculation error: {ex.Message}");
            return "Error";
        }
    }
}