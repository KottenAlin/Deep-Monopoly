# Backlog

## Ready


- record all move for statistical purpus
- add paremeters to bot
- unit test
- add strandard global variables
- add folders for player and board
- elo rating for the bot?

## In progress

## Done
- created basic monopoly game
- implemented basic bot functionality
- trade initiations for bots
- basic statistics for multigame simulation
- - create Neural network
- Implement full bot compatibility
  - add bot house purchasing compaibility
- add house purachsing for bots
- fixing house selling for bots
- colorcode the text
- add trading compatibility
- Only bot monopoly
- Monopoly statistics
- implement neural network
- make conservative and agressive bots
- Devide the program in file
  - add the bot in separate folders



## Problems/Bugs

- ~~board not clearning after turn~~
- ~~players getting multiple turns~~
- ~~players getting multiple turns~~ 
- ~~jumping over and not displaying chance~~
- ~~properties not transfering when bankruptsy~~
- ~~properties not costing money to pay~~


## Optimisation
 - Use less cluttered code 
 - ~~insilaise the bot fewer times~~
 - ~~do not display everything when the bot plays~~



 """
    Evaluate the model on the given data loader.
    
    Args:
        model (torch.nn.Module): The model to evaluate.
        data_loader (torch.utils.data.DataLoader): The data loader for evaluation.
        device (torch.device): The device to perform evaluation on.
        
    Returns:
        float: The average loss over the dataset.
    """
    model.eval()
    total_loss = 0.0
    criterion = torch.nn.CrossEntropyLoss()
    
    with torch.no_grad():
        for batch in data_loader:
            inputs, labels = batch
            inputs, labels = inputs.to(device), labels.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
    
    average_loss = total_loss / len(data_loader)
    return average_loss