const schedule = [
  [
    {
      course: "COMP 445",
      startTime: "13:15",
      endTime: "14:30"
    }
  ],
  [
    {
      course: "COMP 425",
      startTime: "15:30",
      endTime: "17:30"
    },
    {
      course: "COMP 425",
      startTime: "17:45",
      endTime: "20:15"
    }
  ],
  [
    {
      course: "COMP 445",
      startTime: "11:10",
      endTime: "13:00"
    },
    {
      course: "COMP 445",
      startTime: "13:15",
      endTime: "14:30"
    }
  ],
  [
    {
      course: "ENCS 393",
      startTime: "17:45",
      endTime: "20:15"
    }
  ],
  []
];

const timeToFrac = time => {
  const timeSplit = time.split(":");
  return (parseInt(timeSplit[0]) - 7) + (parseInt(timeSplit[1]) / 60);
};

(async () => {
  const $scheduleContainer = $("#scheduleContainer");
  const heightPx = 800;
  const heightHours = 16;
  const pxPerHour = heightPx / heightHours;
  $scheduleContainer.html(schedule.map((dayOfWeek, dowi) => {
    let content = "";
    dayOfWeek.forEach(({ course, startTime, endTime }, i) => {
      const startTimeFrac = timeToFrac(startTime);
      const endTimeFrac = timeToFrac(endTime);
      const paddingTop = i === 0 ? (startTimeFrac * pxPerHour) : 0;
      content += `<div class="courseBlock" style="
        height: ${(endTimeFrac - startTimeFrac) * pxPerHour}px; 
        margin-top: ${paddingTop}px">
        <div><div>${course}</div><div>${startTime} - ${endTime}</div></div>
      </div>`;
      if(i !== dayOfWeek.length - 1) {
        content += `<div class="breakBlock" style="
          height: ${(timeToFrac(dayOfWeek[i + 1].startTime) - endTimeFrac) * pxPerHour}px;
        ">
          <div><input type="radio" name="selectedBreak" value="${`${dowi} - ${startTime}`}"></div>
        </div>`
      }
    });
    return `<div class="dayColumn">${content}</div>`;
  }));
})();

// $("input:radio[name ='selectedBreak']:checked").val();