from ultralytics import YOLO

def train_yolo_model(
    data_yaml="yolo_formatted/dataset.yaml",
    model_size="n",  # n=nano, s=small, m=medium, l=large, x=xlarge
    epochs=100,
    batch_size=16,
    image_size=640,
    device="0"  # GPU device, "cpu" for CPU
):
    """Train YOLO model on UI dataset"""
    # Load base model
    model = YOLO(f'yolov8{model_size}.pt')

    # Train the model
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=image_size,
        device=device,
        name='ui_detector',
        patience=50,  # Early stopping patience
        optimizer='Adam',
        lr0=0.001,
        weight_decay=0.0005
    )

    print("Training completed!")
    print(f"Model saved in: {results.save_dir}")

if __name__ == "__main__":
    train_yolo_model()