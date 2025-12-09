using Microsoft.AspNetCore.SignalR;
using CalculatorBackend.Models;
using CalculatorBackend.Services;

namespace CalculatorBackend.Hubs;

public class CalculatorHub : Hub
{
    private readonly ICalculationEngine _calculator;
    private readonly IExpressionValidator _validator;

    public CalculatorHub(ICalculationEngine calculator, IExpressionValidator validator)
    {
        _calculator = calculator;
        _validator = validator;
    }

    public async Task CalculateExpression(CalculationRequest request)
    {
        var (isValid, error) = _validator.Validate(request.Expression);

        CalculationResponse response;

        if (!isValid)
        {
            response = new CalculationResponse
            {
                Result = "",
                IsValid = false,
                Error = error,
                RequestId = request.RequestId
            };
        }
        else
        {
            var result = _calculator.Evaluate(request.Expression);
            var isError = result.StartsWith("Error");

            response = new CalculationResponse
            {
                Result = result,
                IsValid = !isError,
                Error = isError ? result : null,
                RequestId = request.RequestId
            };
        }

        await Clients.Caller.SendAsync("ReceiveCalculationResult", response);
    }
}
