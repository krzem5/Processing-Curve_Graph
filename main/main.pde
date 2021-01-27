static float minX=-30;
static float maxX=30;
static float minY=-30;
static float maxY=30;
static float points=1000;
float ANGLE=0;
int TIME=0;
float PROC=0;
void setup() {
  size(600, 600);
  strokeCap(ROUND);
}
void draw() {
  background(255);
  stroke(130);
  strokeWeight(2);
  line(0,map(0,minY,maxY,0,height),width,map(0,minY,maxY,0,height));
  line(map(0,minX,maxX,0,width),0,map(0,minX,maxX,0,width),height);
  stroke(0);
  noFill();
  beginShape();
  TIME=0;
  PROC=0;
  for (ANGLE=0; ANGLE<PI*2; ANGLE+=PI*2/points) {
    vertex(map(X(),minX,maxX,0,width),map(Y(),minY,maxY,0,height));
    TIME++;
    PROC=TIME/points;
  }
  endShape();
}
