package example.order;
public final class OrderService {
  private final OrderRepository repository;
  public OrderService(OrderRepository repository) { this.repository = repository; }
  public void createOrder() { repository.save(); }
}
