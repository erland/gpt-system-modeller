package example.order;
public final class OrderResource {
  private final OrderService service;
  public OrderResource(OrderService service) { this.service = service; }
  public void createOrder() { service.createOrder(); }
}
