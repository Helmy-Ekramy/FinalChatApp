namespace CalculatorBackend.Services;

public interface IExpressionValidator
{
    (bool IsValid, string? Error) Validate(string expression);
}
