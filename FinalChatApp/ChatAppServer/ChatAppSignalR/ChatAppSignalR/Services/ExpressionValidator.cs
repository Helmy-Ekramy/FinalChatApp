using System.Text.RegularExpressions;

namespace CalculatorBackend.Services;

public class ExpressionValidator : IExpressionValidator
{
    public (bool IsValid, string? Error) Validate(string expression)
    {
        if (string.IsNullOrWhiteSpace(expression))
        {
            return (true, null); // Empty is valid, will return 0
        }

        // Check for valid characters only (digits, operators, decimal point, spaces)
        if (!Regex.IsMatch(expression, @"^[\d\+\-\*\/\.\s]+$"))
        {
            return (false, "Invalid characters in expression");
        }

        // Check for consecutive operators (++, --, **, //, etc.)
        if (Regex.IsMatch(expression, @"[\+\-\*\/]{2,}"))
        {
            return (false, "Consecutive operators not allowed");
        }

        // Check if expression starts with invalid operator (*, /)
        if (Regex.IsMatch(expression, @"^[\*\/]"))
        {
            return (false, "Expression cannot start with * or /");
        }

        return (true, null);
    }
}
